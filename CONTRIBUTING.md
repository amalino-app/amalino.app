# Helping with Amalino

Thank you! Children read and hear these words every day, so every fix matters. There are three ways to help;
none of them needs programming.

## 1. Translations

- **On Weblate (coming soon):** translate or correct the app and the website in a web form, with no files and no
  git. Sign in, choose your language and suggest a better text. A reviewer for your language approves it.
- **Here on GitHub:** each language has a folder in `translations/`: `app.tsv` is the app, `website.tsv` the
  website. Each line is a key, a tab, and the text. Open the file, press the pencil (Edit), change only the text
  after the tab, and propose the change. GitHub makes the pull request for you.

Please keep:
- every `{placeholder}` exactly as it is in English (for example `{name}`, `{n}`), and `**bold**` and `{app:…}`
  in the website text;
- the key on the left unchanged;
- short words on buttons: children see them on small buttons.

Lines whose key ends in `.zero`, `.one`, `.two`, `.few`, `.many` or `.other` are plural forms; a language leaves
the forms it doesn't use empty.

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
empty texts, the website build). A language's text reaches the app only after a native speaker has checked it,
and the app always ships with every language inside it: nothing is downloaded later.

By contributing you agree that your text is shared under [CC BY-SA 4.0](LICENSE).
