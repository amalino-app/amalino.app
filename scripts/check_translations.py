#!/usr/bin/env python3
"""Checks every translations/<lang>/{app,website}.tsv against English (translations/en/):

  * each line is key<TAB>text (or a # comment),
  * every key exists in the English file and appears once,
  * the {placeholders} are the same as in English (a language may repeat one or use it once),
  * no empty text, except plural rows (keys ending in .zero/.one/.two/.few/.many, never .other): the app
    falls back to <key>.other when a language leaves a form empty,
  * a plural form other than .other may leave out placeholders (Arabic "يوم واحد", English "once") and may
    use {n}; it may not bring in a placeholder its English family doesn't have.

translations/en-US/app.tsv (US spelling) is checked against translations/en/app.tsv the same way.

translations/<lang>/vocab.tsv (the board words): a header row starting id, english, text; every row has a cell per
column, an id appears once, and the text is not empty, not "—" (hidden words are left out of the file) and has no
{placeholder}. Then the Weblate copies (weblate/, scripts/weblate_sync.py): a Weblate text that would be refused is
a problem; Weblate changes not yet in translations/, and Weblate files that are out of date, are only reported.
Run from the repository root: python3 scripts/check_translations.py   (exit code 1 on problems)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSLATIONS = os.path.join(ROOT, 'translations')
PLACEHOLDER = re.compile(r'\{[A-Za-z0-9_:|.\-]+\}')
PLURAL = re.compile(r'\.(zero|one|two|few|many|other)(\.anon)?$')  # sum.days.one.anon: a plural row of the .anon text


def read(path, problems):
    rows = {}
    with open(path, encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) != 2:
                problems.append(f'{path}:{n}: expected key<TAB>text')
                continue
            if parts[0] in rows:
                problems.append(f'{path}:{n}: {parts[0]} appears twice')
            rows[parts[0]] = (n, parts[1])
    return rows


def placeholders(text):
    return sorted(set(PLACEHOLDER.findall(text)))


def family(english, key):
    """The placeholders of every English form of the plural [key], plus {n} (always passed)."""
    def base(k):
        return PLURAL.sub(lambda m: m.group(2) or '', k)
    found = {'{n}'}
    for k, (_, text) in english.items():
        if PLURAL.search(k) and base(k) == base(key):
            found.update(placeholders(text))
    return found


def check_file(path, english, problems):
    rel = os.path.relpath(path, ROOT)
    for key, (n, text) in read(path, problems).items():
        if key not in english:
            problems.append(f'{rel}:{n}: {key} is not in the English file')
            continue
        ref = english[key][1]
        form = PLURAL.search(key)
        minor = form is not None and form.group(1) != 'other'
        if not text.strip():
            if ref.strip() and not minor:
                problems.append(f'{rel}:{n}: {key} is empty')
            continue
        if minor:
            extra = sorted(set(placeholders(text)) - family(english, key))
            if extra:
                problems.append(f'{rel}:{n}: {key} has {extra}, which its English forms don\'t have')
            continue
        if ref.strip() and placeholders(text) != placeholders(ref):
            problems.append(f'{rel}:{n}: {key} has {placeholders(text)}, English has {placeholders(ref)}')


VOCAB_START = ['id', 'english', 'text']


def check_vocab(path, problems):
    rel = os.path.relpath(path, ROOT)
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    header = lines[0].split('\t')
    if header[:3] != VOCAB_START:
        problems.append(f'{rel}:1: the header row must start with {" ".join(VOCAB_START)}')
        return
    seen = set()
    for n, line in enumerate(lines[1:], 2):
        if not line:
            continue
        cells = line.split('\t')
        if len(cells) != len(header):
            problems.append(f'{rel}:{n}: expected {len(header)} cells, got {len(cells)}')
            continue
        cid, text = cells[0], cells[2].strip()
        if cid in seen:
            problems.append(f'{rel}:{n}: {cid} appears twice')
        seen.add(cid)
        if not text:
            problems.append(f'{rel}:{n}: {cid} is empty')
        elif text == '—':
            problems.append(f'{rel}:{n}: {cid} is "—" (a hidden word is left out of the file, never marked)')
        elif PLACEHOLDER.search(text):
            problems.append(f'{rel}:{n}: {cid} has a {{placeholder}}')


def check(folder=TRANSLATIONS):
    problems = []
    for name in ('app.tsv', 'website.tsv'):
        english = read(os.path.join(folder, 'en', name), problems)
        for lang in sorted(os.listdir(folder)):
            path = os.path.join(folder, lang, name)
            if lang == 'en' or not os.path.isfile(path):
                continue
            check_file(path, english, problems)
    for lang in sorted(os.listdir(folder)):
        path = os.path.join(folder, lang, 'vocab.tsv')
        if os.path.isfile(path):
            check_vocab(path, problems)
    return problems


def check_weblate(root=ROOT):
    """(problems, notes) of the Weblate copies (scripts/weblate_sync.py)."""
    import weblate_sync
    rep = weblate_sync.sync(root, write=False)
    problems = [f'{rel}: {unit}: {value!r} would be refused: {why}' for rel, unit, value, why in rep.refused]
    notes = [f'{rel}: {unit}: Weblate {wl!r} and translations/ {tr!r} both changed' for rel, unit, wl, tr in rep.conflicts]
    if rep.taken:
        notes.append(f'{len(rep.taken)} Weblate change(s) are not in translations/ yet: python3 scripts/weblate_sync.py')
    if rep.stale:
        notes.append(f'out of date (translations/ changed): {", ".join(rep.stale)}: python3 scripts/weblate_sync.py')
    notes += rep.notes
    return problems, notes


def main():
    problems = check()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if os.path.isdir(os.path.join(ROOT, 'weblate')):
        wl_problems, notes = check_weblate()
        problems += wl_problems
        for n in notes:
            print('weblate: ' + n)
    for p in problems:
        print(p)
    print('translations: ok' if not problems else f'translations: {len(problems)} problem(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
