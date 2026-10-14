#!/usr/bin/env python3
"""Checks every translations/<lang>/{app,website}.tsv against English (translations/en/):

  * each line is key<TAB>text (or a # comment),
  * every key exists in the English file and appears once,
  * the {placeholders} are the same as in English (a language may repeat one or use it once),
  * no empty text, except plural rows English doesn't use (keys ending in .zero/.one/.two/.few/.many/.other).

translations/en-US/app.tsv (US spelling) is checked against translations/en/app.tsv the same way.
Run from the repository root: python3 scripts/check_translations.py   (exit code 1 on problems)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSLATIONS = os.path.join(ROOT, 'translations')
PLACEHOLDER = re.compile(r'\{[A-Za-z0-9_:|.\-]+\}')
PLURAL = re.compile(r'\.(zero|one|two|few|many|other)$')


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


def check_file(path, english, problems):
    rel = os.path.relpath(path, ROOT)
    for key, (n, text) in read(path, problems).items():
        if key not in english:
            problems.append(f'{rel}:{n}: {key} is not in the English file')
            continue
        ref = english[key][1]
        if not text.strip():
            if not (PLURAL.search(key) and not ref.strip()) and ref.strip():
                problems.append(f'{rel}:{n}: {key} is empty')
            continue
        if ref.strip() and placeholders(text) != placeholders(ref):
            problems.append(f'{rel}:{n}: {key} has {placeholders(text)}, English has {placeholders(ref)}')


def check(folder=TRANSLATIONS):
    problems = []
    for name in ('app.tsv', 'website.tsv'):
        english = read(os.path.join(folder, 'en', name), problems)
        for lang in sorted(os.listdir(folder)):
            path = os.path.join(folder, lang, name)
            if lang == 'en' or not os.path.isfile(path):
                continue
            check_file(path, english, problems)
    return problems


def main():
    problems = check()
    for p in problems:
        print(p)
    print('translations: ok' if not problems else f'translations: {len(problems)} problem(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
