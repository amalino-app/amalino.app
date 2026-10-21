#!/usr/bin/env python3
"""Keeps the Weblate files (weblate/) and the translation files (translations/) in step.

translations/<lang>/{app,website,vocab}.tsv are the source of truth: the website build, the checks and the app's
import read only them. Hosted Weblate can't read TSV, so this script writes a copy of each in a format Weblate
supports well (docs/weblate.md):

    weblate/app/<lang>.json      the app's screens        i18next JSON v4 (plurals as key_one, key_few, ...)
    weblate/website/<lang>.json  the website              i18next JSON v4
    weblate/vocab/<lang>.po      the board words          gettext PO, bilingual: one entry per word, the concept
    weblate/vocab/vocab.pot                               id as msgctxt, its context as #. comments
                                                          (template for a new language)

and reads back what translators changed there:

    python3 scripts/weblate_sync.py            take Weblate's changes into translations/, then rewrite weblate/
    python3 scripts/weblate_sync.py --check    only report (pending Weblate changes, files out of date); exit 1
                                               when a Weblate text would be refused

A change is found per text with a three-way comparison: the Weblate file now, the Weblate file as this script last
wrote it (its git blob is named in weblate/.synced), and what translations/ gives now. Changed only in Weblate: it
goes into translations/ (if it passes the checks below). Changed only in translations/: the Weblate file follows.
Changed on both sides differently: translations/ wins and the Weblate text is printed, so nothing is lost silently.
Only the texts (and their comments and flags) are this script's: the header fields Weblate adds to a PO file on
every commit (PO-Revision-Date, Last-Translator, Language-Team, Plural-Forms, X-Generator) are kept as Weblate wrote
them, so a header-only change is no change and a rewrite doesn't undo it. (Weblate writes the i18next JSON exactly
as this script does, with indentation 2 and unsorted keys, and adds nothing to it.)

A Weblate text is refused (and printed) when it is empty where English isn't, when its {placeholders} differ from
English (a plural form other than "other" may leave some out), when it is a plural form the app has no row for and
it differs from the "other" form (the app never shows it; the owner adds the row), when a board word is "—"
(hidden words are the owner's decision) or contains a tab or a line break, and when Weblate marks it "needs
editing" (fuzzy). Board words are checked again by the app's import (same-board duplicates, length).

English (translations/en/) is read-only in Weblate: it is the source. US English (translations/en-US/) is not on
Weblate; it changes through a pull request. Python 3.9+, nothing to install; git for the three-way comparison.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_translations as ct  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = 'en'
# Languages that stay off Weblate (US English: only the keys whose text differs, maintained by pull request).
NOT_ON_WEBLATE = {'en-US'}
# CLDR plural categories per language, as Weblate shows them for i18next JSON v4. The app picks a form for whole
# numbers only (ru/uk one/few/many, lt one/few/other, ar all six, the others one/other); a category the app has no
# row for is written with the "other" text, so Weblate shows it filled and an unchanged one is ignored.
CLDR = {
    'en': ['one', 'other'], 'da': ['one', 'other'], 'es': ['one', 'many', 'other'],
    'ru': ['one', 'few', 'many', 'other'], 'uk': ['one', 'few', 'many', 'other'], 'lt': ['one', 'few', 'many', 'other'],
    'ar': ['zero', 'one', 'two', 'few', 'many', 'other'],
}
I18N_PLURAL = re.compile(r'^(.*)_(zero|one|two|few|many|other)$')
HIDDEN = '—'
# translations/<lang>/vocab.tsv: the columns this script may change; the others are context, written by the app.
VOCAB_EDITABLE = ('text', 'spoken')
SPOKEN = 'spoken:'
STATE = os.path.join('weblate', '.synced')


# ---------------------------------------------------------------------------------------------------- TSV files

def read_kv(path):
    """OrderedDict {key: text} of a key<TAB>text file (comments left out); {} when absent."""
    out = OrderedDict()
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                if line and not line.startswith('#'):
                    key, _, text = line.partition('\t')
                    out[key] = text
    return out


def read_vocab(path):
    """(header, OrderedDict {id: {column: value}}) of a vocab.tsv; ([], {}) when absent."""
    if not os.path.isfile(path):
        return [], OrderedDict()
    with open(path, encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f if line.strip()]
    header = lines[0].split('\t')
    rows = OrderedDict()
    for line in lines[1:]:
        cells = line.split('\t')
        cells += [''] * (len(header) - len(cells))
        rows[cells[0]] = dict(zip(header, cells))
    return header, rows


def set_kv(path, changes):
    """Writes {key: text} into a key<TAB>text file in place (comments and order kept)."""
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    for i, line in enumerate(lines):
        if line and not line.startswith('#'):
            key = line.partition('\t')[0]
            if key in changes:
                lines[i] = f'{key}\t{changes[key]}'
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))


def set_vocab(path, changes):
    """changes: {(id, column): value}; writes them into vocab.tsv in place."""
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    header = lines[0].split('\t')
    for i, line in enumerate(lines[1:], 1):
        if not line:
            continue
        cells = line.split('\t')
        cells += [''] * (len(header) - len(cells))
        for col in VOCAB_EDITABLE:
            if col in header and (cells[0], col) in changes:
                cells[header.index(col)] = changes[(cells[0], col)]
        lines[i] = '\t'.join(cells)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))


def languages(root):
    folder = os.path.join(root, 'translations')
    return sorted(d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d)) and d not in NOT_ON_WEBLATE)


# ------------------------------------------------------------------------------------------- generated units
# A "unit" is one text in a Weblate file: {unit key: text}. Each generator also returns where the unit lives in
# translations/ ({unit key: (path, key or (id, column))}; None for a plural category the app has no row for) and,
# for the PO files, the context of each word.

class Units:
    def __init__(self):
        self.text = OrderedDict()
        self.target = {}
        self.meta = {}


def plural_groups(keys):
    """{base: {category: TSV key}} of the plural rows (sum.days.one.anon: base sum.days.anon)."""
    groups = OrderedDict()
    for key in keys:
        m = ct.PLURAL.search(key)
        if m:
            base = key[:m.start()] + (m.group(2) or '')
            groups.setdefault(base, {})[m.group(1)] = key
    return groups


def kv_units(root, name, lang):
    path = os.path.join(root, 'translations', lang, name)
    english = read_kv(os.path.join(root, 'translations', SOURCE, name))
    rows = read_kv(path)
    groups = plural_groups(english)
    forms = CLDR.get(lang, ['one', 'other'])
    u = Units()
    done = set()
    for key in english:
        m = ct.PLURAL.search(key)
        if not m:
            u.text[key] = rows.get(key, '')
            u.target[key] = (path, key)
            continue
        base = key[:m.start()] + (m.group(2) or '')
        if base in done:
            continue
        done.add(base)
        other = groups[base].get('other')
        for form in forms:
            tsv_key = groups[base].get(form)
            unit = f'{base}_{form}'
            if tsv_key is not None:
                u.text[unit] = rows.get(tsv_key, '')
                u.target[unit] = (path, tsv_key)
            else:
                u.text[unit] = rows.get(other, '')
                u.target[unit] = None
    return u


def vocab_units(root, lang):
    path = os.path.join(root, 'translations', lang, 'vocab.tsv')
    _, rows = read_vocab(path)
    u = Units()
    for cid, r in rows.items():
        u.text[cid] = r.get('text', '')
        u.target[cid] = (path, (cid, 'text'))
        u.meta[cid] = r
        if 'spoken' in r:
            unit = SPOKEN + cid
            u.text[unit] = r['spoken']
            u.target[unit] = (path, (cid, 'spoken'))
            u.meta[unit] = r
    return u


# ------------------------------------------------------------------------------------------ JSON and PO files

def to_json(units):
    return json.dumps(units.text, ensure_ascii=False, indent=2) + '\n'


def parse_json(text):
    """{unit key: text}; a nested object (if Weblate ever writes one) is flattened with "."."""
    out = {}

    def walk(prefix, value):
        if isinstance(value, dict):
            for k, v in value.items():
                walk(f'{prefix}.{k}' if prefix else k, v)
        elif isinstance(value, str):
            out[prefix] = value
    walk('', json.loads(text) if text.strip() else {})
    return out, set()


def po_quote(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t') + '"'


def po_unquote(s):
    s = s.strip()
    if not (s.startswith('"') and s.endswith('"')):
        raise ValueError(f'not a PO string: {s!r}')
    out, i, body = [], 0, s[1:-1]
    while i < len(body):
        c = body[i]
        if c == '\\' and i + 1 < len(body):
            out.append({'n': '\n', 't': '\t', '"': '"', '\\': '\\'}.get(body[i + 1], body[i + 1]))
            i += 2
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def po_comments(cid, r, lang):
    """The #. lines Weblate shows as the word's description, and its #, flags."""
    if cid.startswith(SPOKEN):
        return [f'Arabic with full tashkeel, as the voice reads it: the vowelled form of «{r.get("text", "")}» '
                f'(English: {r.get("english", "")}). Leave it as it is when unsure.'], []
    where = r.get('folder', '')
    bits = [f'English: {r.get("english", "")}', r.get('class', ''), f'where: {where}' if where else '',
            f'level {r["level"]}' if r.get('level') else '', 'home board (core)' if r.get('core') == 'yes' else '']
    lines = [' · '.join(b for b in bits if b)]
    if r.get('picture'):
        lines.append(f'Picture: {r["picture"]}')
    flags = []
    if r.get('fit'):
        lines.append(f'Button: {r["fit"]}. A shorter word children use is welcome; never a longer one.')
        if r.get('text'):
            flags.append(f'max-length:{len(r["text"])}')
    if r.get('note'):
        lines.append(f'Question: {r["note"]}')
    if r.get('checked') == 'yes':
        lines.append('A native speaker has checked this word.')
    return lines, flags


def po_header(text):
    """[(name, value)] of a PO file's header entry (msgid ""), in its order; [] when it has none."""
    lines, inside = [], False
    for raw in text.split('\n'):
        line = raw.strip()
        if not inside:
            if line == 'msgstr ""':
                inside = True
            elif line.startswith('msgctxt') or (line.startswith('msgid') and line != 'msgid ""'):
                return []
            continue
        if not line.startswith('"'):
            break
        lines.append(po_unquote(line))
    out = []
    for field in ''.join(lines).split('\n'):
        name, sep, value = field.partition(':')
        if sep and name.strip():
            out.append((name.strip(), value.strip()))
    return out


def to_po(units, lang, template=False, keep=None):
    """The PO file of these units. keep: the header fields of the file as it is now ([(name, value)], po_header):
    Weblate adds its own (PO-Revision-Date, Last-Translator, Language-Team, Plural-Forms, X-Generator) on every
    commit, so they stay as Weblate wrote them, in its order; only the fields below are this script's."""
    own = [('Content-Type', 'text/plain; charset=UTF-8'), ('Content-Transfer-Encoding', '8bit')]
    if not template:
        own.append(('Language', lang))
    owned = dict(own)
    fields = [(name, owned.get(name, value)) for name, value in (keep or [])]
    fields += [f for f in own if f[0] not in {name for name, _ in fields}]
    head = ['# Amalino board words. Generated by scripts/weblate_sync.py from translations/<lang>/vocab.tsv;',
            '# translate in Weblate or in vocab.tsv, never both at once. Licence: CC BY-SA 4.0.',
            'msgid ""', 'msgstr ""']
    head += [po_quote(f'{name}: {value}\n') for name, value in fields]
    out = ['\n'.join(head)]
    for unit, text in units.text.items():
        r = units.meta.get(unit, {})
        comments, flags = po_comments(unit, r, lang)
        source = r.get('text', '') if unit.startswith(SPOKEN) else r.get('english', '')
        entry = [f'#. {c}' for c in comments]
        if flags:
            entry.append('#, ' + ', '.join(flags))
        entry += [f'msgctxt {po_quote(unit)}', f'msgid {po_quote(source)}', f'msgstr {po_quote("" if template else text)}']
        out.append('\n'.join(entry))
    return '\n\n'.join(out) + '\n'


def parse_po(text):
    """({msgctxt: msgstr}, {msgctxt of fuzzy entries}); obsolete (#~) entries and the header are left out."""
    out, fuzzy = {}, set()
    entry = {}
    field = None

    def flush():
        if 'msgid' in entry and entry.get('msgctxt') is not None:
            out[entry['msgctxt']] = entry.get('msgstr', entry.get('msgstr[0]', ''))
            if entry.get('fuzzy'):
                fuzzy.add(entry['msgctxt'])
        entry.clear()

    for raw in text.split('\n'):
        line = raw.strip()
        if not line:
            flush()
            field = None
            continue
        if line.startswith('#~'):
            continue
        if line.startswith('#'):
            if field is not None and field != 'comment':
                flush()
            field = 'comment'
            if line.startswith('#,') and 'fuzzy' in [x.strip() for x in line[2:].split(',')]:
                entry['fuzzy'] = True
            continue
        m = re.match(r'^(msgctxt|msgid_plural|msgid|msgstr(?:\[\d+\])?)\s+(".*")$', line)
        if m:
            if m.group(1) in ('msgctxt',) and 'msgid' in entry:
                flush()
            if m.group(1) == 'msgid' and 'msgid' in entry:
                flush()
            field = m.group(1)
            entry[field] = po_unquote(m.group(2))
        elif line.startswith('"') and field in entry:
            entry[field] += po_unquote(line)
    flush()
    return out, fuzzy


# ------------------------------------------------------------------------------------------------- components

def files(root):
    """[(relative path, units, kind)] of every Weblate file translations/ gives now."""
    out = []
    langs = languages(root)
    for name, comp in (('app.tsv', 'app'), ('website.tsv', 'website')):
        for lang in langs:
            if os.path.isfile(os.path.join(root, 'translations', lang, name)):
                out.append((f'weblate/{comp}/{lang}.json', kv_units(root, name, lang), 'json'))
    template = Units()
    for lang in langs:
        if lang == SOURCE or not os.path.isfile(os.path.join(root, 'translations', lang, 'vocab.tsv')):
            continue
        u = vocab_units(root, lang)
        out.append((f'weblate/vocab/{lang}.po', u, 'po'))
        for unit, r in u.meta.items():
            if not unit.startswith(SPOKEN) and unit not in template.text:
                template.text[unit] = ''
                template.meta[unit] = {k: v for k, v in r.items() if k in ('english', 'class', 'folder', 'level', 'core', 'picture')}
    if template.text:
        _, en = read_vocab(os.path.join(root, 'translations', SOURCE, 'vocab.tsv'))
        for unit in template.text:
            if unit in en:
                template.meta[unit] = {k: v for k, v in en[unit].items() if k in ('english', 'class', 'folder', 'level', 'core', 'picture')}
        out.append(('weblate/vocab/vocab.pot', template, 'pot'))
    return out


def render(units, kind, rel, current=None):
    """The text of a Weblate file; current: the file as it is now (a PO file keeps its header fields)."""
    lang = os.path.splitext(os.path.basename(rel))[0]
    if kind == 'json':
        return to_json(units)
    return to_po(units, lang, template=(kind == 'pot'), keep=po_header(current) if current else None)


def parse(text, kind):
    return parse_json(text) if kind == 'json' else parse_po(text)


# ------------------------------------------------------------------------------------------------------- git

def git(root, *args, data=None):
    try:
        r = subprocess.run(['git', '-C', root, *args], input=data, capture_output=True, check=True)
        return r.stdout.decode('utf-8')
    except (OSError, subprocess.CalledProcessError):
        return None


def read_state(root):
    out = {}
    path = os.path.join(root, STATE)
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    rel, _, sha = line.rstrip('\n').partition('\t')
                    out[rel] = sha
    return out


def write_state(root, state):
    with open(os.path.join(root, STATE), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Written by scripts/weblate_sync.py: the git blob of each Weblate file as it last wrote it '
                '(the base of the three-way comparison). Don\'t edit.\n')
        f.writelines(f'{rel}\t{sha}\n' for rel, sha in sorted(state.items()))


# ------------------------------------------------------------------------------------------------------ checks

def check_value(rel, unit, value, target, root):
    """None, or why a Weblate text can't go into translations/."""
    if '\t' in value or '\n' in value:
        return 'has a tab or a line break'
    path, key = target
    if rel.startswith('weblate/vocab/'):
        if value.strip() == HIDDEN:
            return '"—" (a hidden word) is the owner\'s decision'
        if not value.strip():
            return 'empty'
        return None
    name = os.path.basename(path)
    english = {k: (0, v) for k, v in read_kv(os.path.join(root, 'translations', SOURCE, name)).items()}
    ref = english.get(key, (0, ''))[1]
    form = ct.PLURAL.search(key)
    minor = form is not None and form.group(1) != 'other'
    if not value.strip():
        return 'empty' if ref.strip() and not minor else None
    if minor:
        extra = sorted(set(ct.placeholders(value)) - ct.family(english, key))
        return f'has {extra}, which its English forms don\'t have' if extra else None
    if ref.strip() and ct.placeholders(value) != ct.placeholders(ref):
        return f'has {ct.placeholders(value)}, English has {ct.placeholders(ref)}'
    return None


# -------------------------------------------------------------------------------------------------------- sync

class Report:
    def __init__(self):
        self.taken = []      # (rel, unit, old, new)
        self.refused = []    # (rel, unit, value, why)
        self.conflicts = []  # (rel, unit, weblate text, translations/ text)
        self.notes = []
        self.written = []
        self.stale = []      # Weblate files that don't match translations/ (only translations/ changed)


def sync(root=ROOT, write=True, prefer=None):
    """Takes Weblate's changes into translations/ and rewrites weblate/ (write=False: only reports)."""
    rep = Report()
    state = read_state(root)
    tsv_changes = {}  # path -> {key: value}
    for rel, units, kind in files(root):
        path = os.path.join(root, rel)
        if kind == 'pot' or not os.path.isfile(path):
            continue
        with open(path, encoding='utf-8') as f:
            cur, fuzzy = parse(f.read(), kind)
        base = None
        if rel in state:
            blob = git(root, 'cat-file', 'blob', state[rel])
            if blob is not None:
                base = parse(blob, kind)[0]
        if base is None:
            if all(cur.get(u, t) == t for u, t in units.text.items()) or prefer == 'translations':
                continue
            if prefer != 'weblate':
                rep.notes.append(f'{rel}: no record of the last sync (weblate/.synced), so it is unclear which side '
                                 'changed; run with --prefer weblate or --prefer translations')
                continue
            base = dict(units.text)
        for unit in units.text:
            c, b, g = cur.get(unit), base.get(unit), units.text[unit]
            if c is None or c == b or c == g:
                if c is not None and c != g and c == b:
                    rep.stale.append(rel)
                continue
            if unit in fuzzy:
                rep.refused.append((rel, unit, c, 'marked "needs editing" in Weblate'))
                continue
            if g != b:
                rep.conflicts.append((rel, unit, c, g))
                continue
            target = units.target.get(unit)
            if target is None:
                rep.refused.append((rel, unit, c, 'a plural form the app has no row for (the owner adds it)'))
                continue
            why = check_value(rel, unit, c, target, root)
            if why:
                rep.refused.append((rel, unit, c, why))
                continue
            tsv_changes.setdefault(target[0], {})[target[1]] = c
            rep.taken.append((rel, unit, g, c))
        for unit in sorted(set(cur) - set(units.text)):
            rep.notes.append(f'{rel}: {unit} is not in translations/ (left out)')
    rep.stale = sorted(set(rep.stale))
    if not write:
        return rep
    for path, changes in tsv_changes.items():
        (set_vocab if path.endswith('vocab.tsv') else set_kv)(path, changes)
    new_state = dict(state)
    for rel, units, kind in files(root):
        path = os.path.join(root, rel)
        old = None
        if os.path.isfile(path):
            with open(path, encoding='utf-8') as f:
                old = f.read()
        text = render(units, kind, rel, old)
        if old != text:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(text)
            rep.written.append(rel)
        sha = git(root, 'hash-object', '-w', '--', rel)
        if sha:
            new_state[rel] = sha.strip()
    write_state(root, new_state)
    return rep


def pending(root=ROOT):
    """Weblate changes not yet in translations/ (for the app's import and export: run this script first)."""
    rep = sync(root, write=False)
    return rep.taken + [(r, u, '', v) for r, u, v, _ in rep.refused] + [(r, u, g, c) for r, u, c, g in rep.conflicts]


def print_report(rep, check):
    for rel, unit, old, new in rep.taken:
        print(f'{"would take" if check else "taken"}: {rel} {unit}: {old!r} -> {new!r}')
    for rel, unit, value, why in rep.refused:
        print(f'refused: {rel} {unit}: {value!r}: {why}')
    for rel, unit, wl, tr in rep.conflicts:
        print(f'conflict: {rel} {unit}: Weblate {wl!r}, translations/ {tr!r} (translations/ kept)')
    for note in rep.notes:
        print('note: ' + note)
    if check:
        print(f'weblate: {len(rep.taken)} change(s) to take, {len(rep.refused)} refused, {len(rep.conflicts)} conflict(s)')
    else:
        print(f'weblate: {len(rep.taken)} change(s) taken, {len(rep.refused)} refused, {len(rep.conflicts)} conflict(s); '
              f'{len(rep.written)} file(s) rewritten')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--check', action='store_true', help='only report; exit 1 when a Weblate text would be refused')
    ap.add_argument('--prefer', choices=['weblate', 'translations'],
                    help='without a sync record (weblate/.synced): which side wins where they differ')
    a = ap.parse_args(argv)
    rep = sync(ROOT, write=not a.check, prefer=a.prefer)
    print_report(rep, a.check)
    if a.check:
        return 1 if rep.refused or any('no record' in n for n in rep.notes) else 0
    return 1 if any('no record' in n for n in rep.notes) else 0


if __name__ == '__main__':
    sys.exit(main())
