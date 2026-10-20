# Amalino: website, manual and translations

Amalino is a free app that helps children who can't rely on speech to talk: they tap pictures and words, and the
device speaks for them (AAC, augmentative and alternative communication). It works offline, keeps the child's data
on the device, and is free for children and families, always.

This repository holds everything about Amalino that anyone can read and improve:

| Folder | What's in it |
|---|---|
| `site/` | The website, [amalino.app](https://amalino.app): templates, style and the build script |
| `manual/` | The user manual, one folder per language (`manual/en/` first) |
| `translations/` | The words of the app (screens and board words) and the website, one folder per language |
| `weblate/` | A copy of `translations/` for [Hosted Weblate](docs/weblate.md), written by `scripts/weblate_sync.py` |

The app itself is not in this repository.

## Languages

English, Danish, Russian, Ukrainian, Arabic, Spanish and Lithuanian, plus US English spelling (`translations/en-US/`).
English is the source text; the other languages are drafts until a native speaker has checked them.

## How to help

See [CONTRIBUTING.md](CONTRIBUTING.md): fix a translation, improve the manual, or just tell us what's wrong.

## Building the website

Python 3.9 or newer, nothing to install:

```
python3 site/build.py --site https://amalino.app --check   # builds site/dist/ and checks it
python3 -m unittest discover -s site -p 'test_*.py'
python3 scripts/check_translations.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

After a change in `translations/` (or a merged Weblate pull request), `python3 scripts/weblate_sync.py` brings
`weblate/` and `translations/` in step again ([docs/weblate.md](docs/weblate.md)).

Open `site/dist/index.html` in a browser; links work from the file system too.

The manual's pictures (`manual/en/img/`) are drawn from the app on a computer, not a device: the app's
`test/tool/manual_screenshots_test.dart` (an iPad, 820 x 1180, drawn at 2x), then saved as full-colour WebP at
2x (`name-2x.webp`) and half that size (`name-1x.webp`), lossless or quality 85, whichever is smaller. A page
shows one with `![what the picture shows](img/name-1x.webp)` on a line of its own; the build adds the 2x
picture for sharp screens. Limits: 250 KB per file, 4 MB for all of them. A translated manual without its own
`img/` folder shows the English pictures (with its own alt text).

In the manual's Markdown, `{app:key}` is the app's own label in the page's language (`{app:key|label}`: the part
before the first ":"; `{app:key|name=Sam}` fills the string's `{name}`), and `[text](site:privacy)` links to a
website page in the same language. A translated page is marked as a draft until `manual:<page>` is in
`translations/<language>/reviewed.txt` (from the app repository's `content/ui/reviewed.tsv`).

## Licence

The text, translations and manual are under [CC BY-SA 4.0](LICENSE).
