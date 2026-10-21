"""Tests for weblate_sync.py. Run from the repository root: python3 -m unittest discover -s scripts -p 'test_*.py'"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import weblate_sync as ws  # noqa: E402

HAS_GIT = shutil.which('git') is not None

APP = {
    'en': [('about', 'About'), ('hello', 'Hello {name}'), ('days.one', '{n} day'), ('days.few', ''), ('days.other', '{n} days')],
    'da': [('about', 'Om'), ('hello', 'Hej {name}'), ('days.one', '{n} dag'), ('days.few', ''), ('days.other', '{n} dage')],
    'ru': [('about', 'О'), ('hello', 'Привет, {name}'), ('days.one', '{n} день'), ('days.few', '{n} дня'), ('days.other', '{n} дня')],
}
# The header fields Weblate added to weblate/vocab/da.po in its first pull request (#1).
WEBLATE_HEADER = ('"PO-Revision-Date: 2026-10-21 08:47+0000\\n"\n'
                  '"Last-Translator: \\"amalino.app\\" <hello@amalino.app>\\n"\n'
                  '"Language-Team: Danish <https://hosted.weblate.org/projects/amalino/board-words/da/>\\n"\n'
                  '"Plural-Forms: nplurals=2; plural=n != 1;\\n"\n'
                  '"X-Generator: Weblate 2026.11.dev0\\n"\n')
VOCAB_HEAD = ['id', 'english', 'text', 'class', 'folder', 'level', 'core', 'picture', 'fit', 'checked', 'note']
VOCAB = {
    'en': [['apple', 'apple', 'apple', 'noun', 'food', '1', 'no', 'https://static.arasaac.org/pictograms/2462/2462_300.png', '', '', '']],
    'da': [['apple', 'apple', 'æble', 'noun', 'food', '1', 'no', 'https://static.arasaac.org/pictograms/2462/2462_300.png',
            'must shorten: cut on S8+ portrait 36', 'yes', 'Is "æble" the word a child says?'],
           ['say "hi"', 'say "hi"', 'sig "hej"\\', 'verb', 'core', '1', 'yes', '', '', '', '']],
}


def write(root, lang, name, rows):
    os.makedirs(os.path.join(root, 'translations', lang), exist_ok=True)
    with open(os.path.join(root, 'translations', lang, name), 'w', encoding='utf-8') as f:
        if name == 'vocab.tsv':
            f.write('\t'.join(VOCAB_HEAD) + '\n' + ''.join('\t'.join(r) + '\n' for r in rows))
        else:
            f.write('# key\ttext\n' + ''.join(f'{k}\t{v}\n' for k, v in rows))


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


class Formats(unittest.TestCase):
    def test_po_round_trip_keeps_quotes_and_backslashes(self):
        u = ws.Units()
        u.text['say "hi"'] = 'sig "hej"\\ og\tså'
        u.meta['say "hi"'] = {'english': 'say "hi"', 'class': 'verb', 'fit': 'must shorten', 'text': 'sig'}
        text = ws.to_po(u, 'da')
        self.assertIn('#, max-length:3', text)
        units, fuzzy = ws.parse_po(text)
        self.assertEqual(units, {'say "hi"': 'sig "hej"\\ og\tså'})
        self.assertEqual(fuzzy, set())

    def test_po_as_weblate_writes_it(self):
        text = ('msgid ""\nmsgstr ""\n"Language: da\\n"\n\n#. English: apple\n#, fuzzy, max-length:4\nmsgctxt "apple"\n'
                'msgid "apple"\nmsgstr ""\n"æb"\n"let"\n#~ msgctxt "old"\n#~ msgid "old"\n#~ msgstr "gammel"\n\n'
                'msgctxt "pear"\nmsgid "pear"\nmsgstr "pære"\n')
        units, fuzzy = ws.parse_po(text)
        self.assertEqual(units, {'apple': 'æblet', 'pear': 'pære'})
        self.assertEqual(fuzzy, {'apple'})

    def test_po_header_keeps_weblate_fields_in_their_order(self):
        u = ws.Units()
        u.text['pear'] = 'pære'
        u.meta['pear'] = {'english': 'pear'}
        keep = ws.po_header(ws.to_po(u, 'da').replace('"Language: da\\n"\n', '"Language: dk\\n"\n' + WEBLATE_HEADER))
        self.assertEqual([n for n, _ in keep], ['Content-Type', 'Content-Transfer-Encoding', 'Language', 'PO-Revision-Date',
                                                'Last-Translator', 'Language-Team', 'Plural-Forms', 'X-Generator'])
        self.assertEqual(dict(keep)['Last-Translator'], '"amalino.app" <hello@amalino.app>')
        text = ws.to_po(u, 'da', keep=keep)
        self.assertIn('"Language: da\\n"\n' + WEBLATE_HEADER, text)  # the script's own fields are its own again
        self.assertEqual(ws.parse_po(text)[0], {'pear': 'pære'})
        self.assertEqual(ws.po_header('msgctxt "a"\nmsgid "a"\nmsgstr "b"\n'), [])

    def test_nested_json_is_flattened(self):
        self.assertEqual(ws.parse_json('{"a": {"b": "x", "c_one": "y"}, "d.e": "z"}')[0], {'a.b': 'x', 'a.c_one': 'y', 'd.e': 'z'})

    def test_plural_rows_become_cldr_categories(self):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        for lang, rows in APP.items():
            write(root, lang, 'app.tsv', rows)
        en = ws.kv_units(root, 'app.tsv', 'en')
        self.assertEqual(list(en.text), ['about', 'hello', 'days_one', 'days_other'])
        ru = ws.kv_units(root, 'app.tsv', 'ru')
        self.assertEqual(list(ru.text), ['about', 'hello', 'days_one', 'days_few', 'days_many', 'days_other'])
        # No .many row: Weblate shows the "other" text; the unit has no row to go back to.
        self.assertEqual(ru.text['days_many'], '{n} дня')
        self.assertIsNone(ru.target['days_many'])
        self.assertEqual(ru.target['days_few'][1], 'days.few')


@unittest.skipUnless(HAS_GIT, 'needs git')
class Sync(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root)
        for lang, rows in APP.items():
            write(self.root, lang, 'app.tsv', rows)
            write(self.root, lang, 'website.tsv', [('home', {'en': 'Home', 'da': 'Hjem', 'ru': 'Главная'}[lang])])
        for lang, rows in VOCAB.items():
            write(self.root, lang, 'vocab.tsv', rows)
        os.makedirs(os.path.join(self.root, 'translations', 'en-US'))
        with open(os.path.join(self.root, 'translations', 'en-US', 'app.tsv'), 'w', encoding='utf-8') as f:
            f.write('# key\ttext\n')
        self.git('init', '-q')
        ws.sync(self.root)
        self.commit()

    def git(self, *args):
        subprocess.run(['git', '-C', self.root, '-c', 'user.name=t', '-c', 'user.email=t@t', *args], check=True,
                       capture_output=True)

    def commit(self):
        self.git('add', '-A')
        self.git('commit', '-qm', 'sync')

    def path(self, rel):
        return os.path.join(self.root, rel)

    def edit_json(self, rel, **changes):
        d = json.loads(read(self.path(rel)))
        d.update({k.replace('__', '.'): v for k, v in changes.items()})
        with open(self.path(rel), 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=4)  # Weblate's own formatting may differ

    def test_files_written(self):
        for rel in ['weblate/app/en.json', 'weblate/app/da.json', 'weblate/website/ru.json', 'weblate/vocab/da.po',
                    'weblate/vocab/vocab.pot', 'weblate/.synced']:
            self.assertTrue(os.path.isfile(self.path(rel)), rel)
        self.assertFalse(os.path.exists(self.path('weblate/vocab/en.po')), 'English is the source, not a translation')
        self.assertFalse(os.path.exists(self.path('weblate/app/en-US.json')), 'US English stays off Weblate')
        po = read(self.path('weblate/vocab/da.po'))
        self.assertIn('#. English: apple · noun · where: food · level 1', po)
        self.assertIn('#. Question: Is "æble" the word a child says?', po)
        self.assertIn('#, max-length:4', po)
        self.assertIn('msgctxt "apple"\nmsgid "apple"\nmsgstr "æble"', po)
        self.assertIn('msgctxt "apple"\nmsgid "apple"\nmsgstr ""', read(self.path('weblate/vocab/vocab.pot')))
        rep = ws.sync(self.root, write=False)
        self.assertEqual((rep.taken, rep.refused, rep.conflicts, rep.notes), ([], [], [], []))

    def test_weblate_changes_come_back_and_bad_ones_are_refused(self):
        self.edit_json('weblate/app/da.json', about='Om appen', hello='Hej', days_two='{n} dage')
        self.edit_json('weblate/app/ru.json', days_few='{n} дня.', days_many='{n} дней')
        po = read(self.path('weblate/vocab/da.po')).replace('msgstr "æble"', 'msgstr "æblet"')
        po = po.replace('msgstr "sig \\"hej\\"\\\\"', 'msgstr "—"')
        with open(self.path('weblate/vocab/da.po'), 'w', encoding='utf-8') as f:
            f.write(po)
        self.assertEqual(len(ws.pending(self.root)), 6)
        rep = ws.sync(self.root)
        self.assertEqual(sorted((r, u) for r, u, _o, _n in rep.taken),
                         [('weblate/app/da.json', 'about'), ('weblate/app/ru.json', 'days_few'), ('weblate/vocab/da.po', 'apple')])
        self.assertIn('weblate/app/da.json: days_two is not in translations/ (left out)', rep.notes)
        why = {u: w for _r, u, _v, w in rep.refused}
        self.assertIn("English has ['{name}']", why['hello'])
        self.assertIn('no row', why['days_many'])
        self.assertIn('owner', why['say "hi"'])
        self.assertIn('about\tOm appen\n', read(self.path('translations/da/app.tsv')))
        self.assertIn('days.few\t{n} дня.\n', read(self.path('translations/ru/app.tsv')))
        self.assertIn('hello\tHej {name}\n', read(self.path('translations/da/app.tsv')))
        vocab = read(self.path('translations/da/vocab.tsv'))
        self.assertIn('apple\tapple\tæblet\tnoun', vocab)
        self.assertIn('sig "hej"\\', vocab)
        # The Weblate files follow translations/ again; nothing is pending.
        self.assertEqual(json.loads(read(self.path('weblate/app/da.json')))['hello'], 'Hej {name}')
        self.assertEqual(ws.pending(self.root), [])

    def weblate_po(self, *replace):
        """Writes weblate/vocab/da.po as Weblate commits it: its header fields added, and the given changes."""
        po = read(self.path('weblate/vocab/da.po')).replace('"Language: da\\n"\n', '"Language: da\\n"\n' + WEBLATE_HEADER)
        for old, new in replace:
            po = po.replace(old, new)
        with open(self.path('weblate/vocab/da.po'), 'w', encoding='utf-8') as f:
            f.write(po)
        return po

    def test_a_header_only_change_is_not_a_change(self):
        po = self.weblate_po()
        rep = ws.sync(self.root, write=False)
        self.assertEqual((rep.taken, rep.refused, rep.conflicts, rep.notes, rep.stale), ([], [], [], [], []))
        rep = ws.sync(self.root)
        self.assertEqual(rep.written, [])
        self.assertEqual(read(self.path('weblate/vocab/da.po')), po)

    def test_rewrite_keeps_weblates_header(self):
        po = self.weblate_po(('msgstr "æble"', 'msgstr "æblet"'))
        rep = ws.sync(self.root)
        self.assertEqual([(r, u) for r, u, _o, _n in rep.taken], [('weblate/vocab/da.po', 'apple')])
        po = po.replace('max-length:4', 'max-length:5')  # the word's current length: the entries are the script's
        self.assertEqual(read(self.path('weblate/vocab/da.po')), po)
        self.assertIn('apple\tapple\tæblet\tnoun', read(self.path('translations/da/vocab.tsv')))
        self.commit()
        # A change from translations/ rewrites the entries; Weblate's header stays as it is.
        vocab = read(self.path('translations/da/vocab.tsv')).replace('\tæblet\t', '\tæbler\t')
        with open(self.path('translations/da/vocab.tsv'), 'w', encoding='utf-8') as f:
            f.write(vocab)
        self.assertEqual(ws.sync(self.root, write=False).stale, ['weblate/vocab/da.po'])
        ws.sync(self.root)
        self.assertEqual(read(self.path('weblate/vocab/da.po')), po.replace('msgstr "æblet"', 'msgstr "æbler"'))
        # Right after a sync, --check is clean and a second sync writes nothing.
        rep = ws.sync(self.root, write=False)
        self.assertEqual((rep.taken, rep.refused, rep.conflicts, rep.notes, rep.stale), ([], [], [], [], []))
        self.assertEqual(ws.sync(self.root).written, [])

    def test_translations_changes_reach_weblate(self):
        with open(self.path('translations/da/website.tsv'), 'w', encoding='utf-8') as f:
            f.write('# key\ttext\nhome\tForside\n')
        rep = ws.sync(self.root, write=False)
        self.assertEqual(rep.stale, ['weblate/website/da.json'])
        self.assertEqual(ws.pending(self.root), [])
        ws.sync(self.root)
        self.assertEqual(json.loads(read(self.path('weblate/website/da.json'))), {'home': 'Forside'})

    def test_both_sides_changed_keeps_translations(self):
        self.edit_json('weblate/website/ru.json', home='Домой')
        with open(self.path('translations/ru/website.tsv'), 'w', encoding='utf-8') as f:
            f.write('# key\ttext\nhome\tНачало\n')
        rep = ws.sync(self.root)
        self.assertEqual([(u, c, g) for _r, u, c, g in rep.conflicts], [('home', 'Домой', 'Начало')])
        self.assertIn('home\tНачало', read(self.path('translations/ru/website.tsv')))

    def test_without_a_sync_record_it_asks(self):
        os.remove(self.path('weblate/.synced'))
        self.edit_json('weblate/app/da.json', about='Om appen')
        rep = ws.sync(self.root, write=False)
        self.assertTrue(any('no record' in n for n in rep.notes))
        rep = ws.sync(self.root, prefer='weblate')
        self.assertIn('about\tOm appen\n', read(self.path('translations/da/app.tsv')))


class RealFiles(unittest.TestCase):
    def test_the_weblate_files_match_translations(self):
        if not os.path.isfile(os.path.join(ws.ROOT, ws.STATE)):
            self.skipTest('no weblate/ yet')
        rep = ws.sync(ws.ROOT, write=False)
        self.assertEqual(rep.refused, [], 'a Weblate text that would be refused')


if __name__ == '__main__':
    unittest.main()
