# Translating on Hosted Weblate

Volunteers correct the app's screens, the website and the board words in a web form on
[Hosted Weblate](https://hosted.weblate.org), with no files and no git. This page says how it is set up: which
files Weblate reads, how its changes come back, and what the owner does once.

## How it fits together

`translations/<lang>/` stays the source of truth: the website build, `scripts/check_translations.py` and the app's
import (`tools/content/import_public.py` in the app repository) read only those files. Weblate can't read TSV
(its CSV format guesses the delimiter and has no plurals or per-word context), so `scripts/weblate_sync.py` writes
a copy of each file in a format Weblate supports well, and reads Weblate's changes back:

| What | Source of truth | Weblate copy | Weblate format |
|---|---|---|---|
| App screens | `translations/<lang>/app.tsv` | `weblate/app/<lang>.json` | i18next JSON v4 |
| Website | `translations/<lang>/website.tsv` | `weblate/website/<lang>.json` | i18next JSON v4 |
| Board words | `translations/<lang>/vocab.tsv` | `weblate/vocab/<lang>.po` (+ `vocab.pot`) | gettext PO |
| Manual | `manual/<lang>/*.md` | none: pull requests only | |

```
Weblate ──PR──▶ weblate/*  ──scripts/weblate_sync.py──▶ translations/*  ──import_public.py──▶ the app's content
                weblate/*  ◀──scripts/weblate_sync.py──  translations/*  ◀──export_public.py──  the app's content
```

The sync compares each text three ways: the Weblate file now, the Weblate file as the sync last wrote it (its git
blob is in `weblate/.synced`), and what `translations/` gives now. Changed only in Weblate: it goes into
`translations/` if it passes the checks. Changed only in `translations/` (a GitHub pull request, or a new export
from the app): the Weblate file follows. Changed on both sides differently: `translations/` wins and the Weblate
text is printed, so nothing is lost without a trace. The sync owns the texts, not the PO header: the fields Weblate adds on every
commit (`PO-Revision-Date`, `Last-Translator`, `Language-Team`, `Plural-Forms`, `X-Generator`) stay as Weblate
wrote them, so a sync after a Weblate pull request leaves them alone. Refused and printed: an empty text where English has one,
different `{placeholders}`, a board word "—" (hiding a word is the owner's decision), a text Weblate marks "needs
editing", and a plural form the app has no row for that differs from the "other" form.

### Why these formats

- **App screens and website: i18next JSON v4** (Weblate id `i18nextv4`). Monolingual, one flat file per
  language with `en.json` as the base, and plurals stored with the CLDR category names, which are exactly the app's
  own: `days.one` / `days.few` / `days.many` / `days.other` in the TSV are `days_one` … `days_other` in the JSON
  (the "your child" wording `sum.days.one.anon` is `sum.days.anon_one`). Weblate shows each language the forms
  CLDR gives it: Danish and English one/other, Spanish one/many/other, Russian, Ukrainian and Lithuanian
  one/few/many/other, Arabic all six. A form the app has no row for (Spanish "many", Lithuanian "many", and
  others) is written with the "other" text so Weblate shows it filled; the app never shows it for whole numbers.
  Gettext PO was the alternative, but it numbers plural forms by each language's Plural-Forms formula instead of
  naming them, so mapping them to the app's rows would be fragile.
- **Board words: gettext PO, bilingual** (Weblate id `po`). Each language has its own file with only the words a
  child sees in that language (hidden words are left out, so nobody "translates" them), the concept id as
  `msgctxt` (two words may share an English label), the English label as `msgid`, and the context Weblate shows
  next to the word as `#.` comments: part of speech, folder, level, home-board word, the picture's address, the
  long-label note and the reviewer's question. A word that doesn't fit its button carries `#, max-length:N` (its
  current length), so Weblate warns about a longer one. Arabic has a second entry per word, `spoken:<id>`, for the
  vowelled form the voice reads.
- **Manual: pull requests only.** Weblate can translate Markdown, but then Weblate is the source: it splits a page
  into paragraphs, translates them one by one and doesn't read changes made in the files. Our translated pages are
  written as natural text, not sentence by sentence, with `{app:key}` for every app label; reviewers fix them on
  GitHub.
- **US English** (`translations/en-US/`) holds only the texts that differ from British English; it stays off
  Weblate and changes by pull request (the owner keeps the word pairs).

The Weblate files are generated: on GitHub, edit `translations/`, never `weblate/`.

## Components to create

Project **Amalino** (slug `amalino`), website `https://amalino.app`, licence CC BY-SA 4.0. Create `app` first from
the repository; the others use the same repository through `weblate://amalino/app`.

| Setting | `app` (App screens) | `website` (Website) | `vocab` (Board words) |
|---|---|---|---|
| Version control | GitHub (Hosted Weblate GitHub app) | `weblate://amalino/app` | `weblate://amalino/app` |
| Repository | `https://github.com/amalino-app/amalino.app` | | |
| Repository branch | `main` | | |
| File format | i18next JSON v4 | i18next JSON v4 | gettext PO file |
| File mask | `weblate/app/*.json` | `weblate/website/*.json` | `weblate/vocab/*.po` |
| Monolingual base language file | `weblate/app/en.json` | `weblate/website/en.json` | (empty) |
| Template for new translations | `weblate/app/en.json` | `weblate/website/en.json` | `weblate/vocab/vocab.pot` |
| Edit base file | off (English is read-only) | off | n/a |
| Language filter | `^(da\|ru\|uk\|ar\|es\|lt)$` | `^(da\|ru\|uk\|ar\|es\|lt)$` | `^(da\|ru\|uk\|ar\|es\|lt)$` |
| Language code style | Default (`da`, `ru` …: the folder names) | same | same |
| Adding new translation | Contact maintainers | Contact maintainers | Contact maintainers |
| Translation flags | `placeholders:r"\{[A-Za-z0-9_:\|.\-]+\}"` | `placeholders:r"\{[A-Za-z0-9_:\|.\-]+\}", md-text` | `ignore-same` |
| Enforced checks | Placeholders | Placeholders | Maximum length |
| File format parameters | JSON indentation 2, don't sort keys | same | PO line wrapping: no wrapping |

- **Placeholders:** `{name}`, `{n}`, `{app:key}` stay exactly as in English. In the website, `**bold**` stays bold
  and `[[link text]]` keeps its double brackets (`md-text` checks Markdown).
- **Plural forms** come from Weblate's CLDR rules for i18next v4. After the first import, open one plural string
  (`days`) in Russian (expect one/few/many/other) and Arabic (six forms) to confirm.
- **Board words:** `ignore-same`, because many words are the same in English (pizza, taxi). Don't install the
  "Update PO files to match POT (msgmerge)" add-on: it would add the hidden words to every language.
- **Instructions** shown to translators (component "Translation instructions"): *A child taps these words and
  hears them. Write the word a child hears at home, short enough for a small button. Unsure? Leave it, or use a
  suggestion. Don't change {placeholders}.*
- **Commit, push, pull requests:** "Push on commit" on, "Create merge requests" (pull requests) on, "Merge pull
  requests automatically" off: the owner approves every change. Commit message: `Translations from Weblate
  ({{ language_name }}): {{ component_name }}`. Optional add-on: "Squash Git commits" (per language).
- **Reviews:** Weblate's "approved" state isn't stored in JSON or PO, so it doesn't reach the app. A native
  speaker's approval is still recorded by the owner (`reviewed.txt`: an app key, `vocab:<id>` for a board word,
  `web:<key>` for the website).

## What the owner does once

1. **Sign up** at [hosted.weblate.org](https://hosted.weblate.org) with the GitHub account that owns
   `amalino-app`.
2. **Install the Hosted Weblate GitHub app** (Weblate: your profile → Account → connect GitHub, or the "GitHub"
   option when adding a component) for the `amalino-app` organisation, with access to `amalino.app` only. The app
   clones the repository, receives push notifications, pushes the translation branch and opens the pull requests,
   so no deploy key or extra collaborator is needed. (The fallback without the app: invite the GitHub user
   `weblate`, e-mail hosted@weblate.org, and use the SSH address `git@github.com:amalino-app/amalino.app.git`.)
3. **Push `main`** with `weblate/` and `weblate/.synced` in it (`python3 scripts/weblate_sync.py` writes them).
4. **Create the project** ("Add new translation project"): name Amalino, slug `amalino`, website
   `https://amalino.app`, licence "Creative Commons Attribution Share Alike 4.0", contributor agreement: *By
   contributing you agree that your text is shared under CC BY-SA 4.0.*
5. **Choose the Libre plan** (gratis for public libre projects, the same limits as the 160k-strings plan; this
   project has about 25,000: some 1,050 app texts, 124 website texts and 2,600 words, times six languages, plus the
   Arabic spoken forms) and press
   **Request project approval**. Say: a free, non-commercial app that helps children who can't rely on speech to
   talk; translations, website and manual are public under CC BY-SA 4.0 in `amalino-app/amalino.app`; volunteers
   translate into Danish, Russian, Ukrainian, Arabic, Spanish and Lithuanian. *Open question:* Weblate grants
   the Libre plan to projects under a libre licence; the translations are CC BY-SA, but the app's code is closed.
   If Weblate declines for that reason, the GitHub and spreadsheet paths keep working (CONTRIBUTING.md), and a
   paid plan or a self-hosted Weblate use the same setup.
6. **Create the three components** with the table above (`app` first), then check one plural string in Russian
   and Arabic, and one board word's description (English, folder, picture link).
7. **Teams:** give each language a reviewer when a native speaker volunteers ("Users" → Reviewers per language);
   everyone else makes suggestions or translations, which come to `main` only through pull requests.

## What the owner does for each Weblate pull request

1. Read the pull request on GitHub (it changes only `weblate/`). The "Check" run lists texts that would be refused
   (placeholders, empty, "—"); fix those in Weblate or leave them: the sync prints and skips them.
2. Merge it, then on your computer:
   ```
   git pull
   python3 scripts/weblate_sync.py      # takes the changes into translations/, rewrites weblate/
   python3 scripts/check_translations.py
   git commit -am "Translations from Weblate (#<pull request>)" && git push
   ```
3. In the app repository: `python3 tools/content/import_public.py ../amalino.app --dry-run` (the diff, the
   refused words: same-board duplicates, length warnings), then without `--dry-run`; rebuild the content, check it
   in the app, record native approvals in `content/ui/reviewed.tsv`; then `python3 tools/content/export_public.py
   ../amalino.app` (it refuses to run while Weblate changes are waiting), and commit both repositories.

The website text has no app step: step 2 is enough, and the next build publishes it.

## For the command line

`.weblate` in the repository root is the configuration of [wlc](https://docs.weblate.org/en/latest/wlc.html),
Weblate's command-line client: `wlc stats`, `wlc pull`, `wlc commit` and `wlc push` work on this project from the
repository folder (with an API key in `~/.config/weblate`).
