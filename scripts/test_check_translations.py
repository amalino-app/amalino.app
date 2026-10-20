"""Tests for check_translations.py. Run from the repository root: python3 -m unittest discover -s scripts -p 'test_*.py'"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import check_translations as ct  # noqa: E402


def write(folder, lang, rows, name='app.tsv'):
    os.makedirs(os.path.join(folder, lang), exist_ok=True)
    with open(os.path.join(folder, lang, name), 'w', encoding='utf-8') as f:
        f.write('# key\ttext\n' + ''.join(f'{k}\t{v}\n' for k, v in rows))


class CheckTranslations(unittest.TestCase):
    def test_the_real_files_pass(self):
        self.assertEqual(ct.check(), [])

    def test_problems_are_found(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'en', [('hi', 'Hello {name}'), ('n.two', ''), ('bye', 'Bye')])
            write(d, 'en', [('t', 'Text')], 'website.tsv')
            write(d, 'da', [('hi', 'Hej'), ('n.two', ''), ('bye', ''), ('new', 'x')])
            write(d, 'es', [('bye', 'Adiós'), ('bye', 'Chao')])
            write(d, 'ru', [('hi', 'Привет {name}, {name}'), ('n.two', 'два {n}')])
            problems = ct.check(d)
        text = '\n'.join(problems)
        self.assertIn('da/app.tsv:2: hi has [], English has', text)
        self.assertIn('da/app.tsv:4: bye is empty', text)
        self.assertIn('da/app.tsv:5: new is not in the English file', text)
        self.assertIn('es/app.tsv:3: bye appears twice', text)
        self.assertNotIn('n.two', text)
        self.assertNotIn('ru/', text)

    def test_plural_forms(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'en', [('d.one', 'Once.'), ('d.few', ''), ('d.other', '{n} times for {name}.')])
            write(d, 'en', [('t', 'Text')], 'website.tsv')
            write(d, 'ar', [('d.one', 'مرة واحدة {n}'), ('d.few', ''), ('d.other', 'مرات: {n}')])
            write(d, 'lt', [('d.one', ''), ('d.few', '{n} kartai {who}'), ('d.other', '')])
            problems = ct.check(d)
        text = '\n'.join(problems)
        self.assertNotIn('ar/app.tsv:2', text)
        self.assertIn("ar/app.tsv:4: d.other has ['{n}'], English has", text)
        self.assertNotIn('lt/app.tsv:2', text)
        self.assertIn("lt/app.tsv:3: d.few has ['{who}']", text)
        self.assertIn('lt/app.tsv:4: d.other is empty', text)

    def test_vocab(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'en', [('hi', 'Hello')])
            write(d, 'en', [('t', 'Text')], 'website.tsv')
            os.makedirs(os.path.join(d, 'da'))
            with open(os.path.join(d, 'da', 'vocab.tsv'), 'w', encoding='utf-8') as f:
                f.write('id\tenglish\ttext\tclass\n'
                        'apple\tapple\tæble\tnoun\n'
                        'apple\tapple\tæble\tnoun\n'
                        'pear\tpear\t\tnoun\n'
                        'it\tit\t—\tpronoun\n'
                        'x\tx\t{n}\tnoun\n'
                        'y\ty\ty\n')
            text = '\n'.join(ct.check(d))
        self.assertIn('da/vocab.tsv:3: apple appears twice', text)
        self.assertIn('da/vocab.tsv:4: pear is empty', text)
        self.assertIn('da/vocab.tsv:5: it is "—"', text)
        self.assertIn('da/vocab.tsv:6: x has a {placeholder}', text)
        self.assertIn('da/vocab.tsv:7: expected 4 cells, got 3', text)


if __name__ == '__main__':
    unittest.main()
