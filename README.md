# Amalino: website, manual and translations

Amalino is a free app that helps children who can't rely on speech to talk: they tap pictures and words, and the
device speaks for them (AAC, augmentative and alternative communication). It works offline, keeps the child's data
on the device, and is free for children and families, always.

This repository holds everything about Amalino that anyone can read and improve:

| Folder | What's in it |
|---|---|
| `site/` | The website, [amalino.app](https://amalino.app): templates, style and the build script |
| `manual/` | The user manual, one folder per language (`manual/en/` first) |
| `translations/` | The words of the app and the website, one folder per language |

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
```

Open `site/dist/index.html` in a browser; links work from the file system too.

## Licence

The text, translations and manual are under [CC BY-SA 4.0](LICENSE).
