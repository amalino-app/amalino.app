# Helping with Amalino

Thank you! Children read and hear these words every day, so every fix matters. There are three ways to help;
none of them needs programming.

## 1. Translations

There are three kinds of text: the app's screens, the website, and the **board words**, the words a child taps
and hears.

- **On Weblate:** [Translate on Weblate](https://hosted.weblate.org/engage/amalino/). Weblate is a website where
  you correct all three in your browser, with no files and no git; a free account is enough. Choose your language
  and suggest a better text. Each board word shows its English word, its folder, its picture and, when it's too
  long for its button, a note. The owner checks every suggestion before it goes into the app.
  [How it is set up](docs/weblate.md).
- **Here on GitHub:** each language has a folder in `translations/`: `app.tsv` is the app, `website.tsv` the
  website, `vocab.tsv` the board words. In `app.tsv` and `website.tsv` each line is a key, a tab, and the text;
  `vocab.tsv` is a table (GitHub shows it with a search box) where only the `text` column is yours to change
  (Arabic: also `spoken`, the word with full tashkeel as the voice reads it). Open the file, press the pencil
  (Edit), change only that text, and propose the change. GitHub makes the pull request for you. Don't edit the
  `weblate/` folder: it is written from `translations/`.
- **With a spreadsheet:** if you'd rather not use either, the [Help translate](https://amalino.app/en/translate/)
  page explains how to check your language in a spreadsheet and send it back by e-mail. That stays open to
  everyone.

Please keep:
- every `{placeholder}` exactly as it is in English (for example `{name}`, `{n}`), and `**bold**` and `{app:…}`
  in the website text;
- the key or id on the left unchanged;
- short words on buttons: children see them on small buttons. A board word is the word a child hears at home,
  one or two words; a word marked "must shorten" doesn't fit its button, so a shorter word children use is very
  welcome.

Lines whose key ends in `.zero`, `.one`, `.two`, `.few`, `.many` or `.other` are plural forms; a language leaves
the forms it doesn't use empty. A word that isn't in your language's `vocab.tsv` is hidden in that language on
purpose (for example "the" in Russian): write to us if you think a child needs it.

## 2. The manual

The manual is in `manual/<language>/`, one page per topic. Open a page, press the pencil (Edit), fix it, and
propose the change. To translate the manual into your language, copy `manual/en/` to a new folder and translate
page by page. Write every button, menu and setting the page names as `{app:key}` (the key of that text in
`translations/<language>/app.tsv`, for example `**{app:historyBackups}**`): the site then shows the app's own
words, so the manual and the app never disagree. A translated page shows a "draft translation" note until a native
speaker has checked it.

## 3. Everyone else

If you'd rather not use GitHub at all, write to hello@amalino.app with the language, the place (screen or page) and what
should change. Spreadsheets are welcome too.

## What happens next

Only the project owner merges changes. Automatic checks look at every pull request first (keys, placeholders,
empty texts, the board words, the website build); the app's import checks the board words again, for example
that no board gets two buttons with the same word. A language's text reaches the app only after a native speaker has checked it,
and the app always ships with every language inside it: nothing is downloaded later.

By contributing you agree that your text is shared under [CC BY-SA 4.0](LICENSE).
