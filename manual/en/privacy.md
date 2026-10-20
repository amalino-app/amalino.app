<!-- description: What Amalino keeps on the device, what it downloads and when, and what (if anything) leaves the device. No ads, no tracking, no account. -->
# Privacy

Amalino is built so the child's words stay with the child. There are no ads, no tracking and no account.

## What stays on the device

- The child's boards, words, photos and recordings.
- What the child says, and the usage logs behind **Progress** and its **This week** summary.
- The child's name.

All of it is stored only on the device, encrypted. It is never sent to me.

## Backups

- **The automatic daily backup** stays on the device and opens only there.
- **Export backup** makes a file protected by your password, to move to a new device. Where you keep it is up to you.
- **iPhone and iPad**: if you back up the device to iCloud or a computer, Amalino's data is part of that backup.
- **Android**: Amalino's data isn't copied to your Google backup or to a new phone.

See [Sharing and printing](sharing-and-printing.md).

## What Amalino downloads

Some things are downloaded once, when you ask for them, and then work offline. Nothing about the child is sent.

- **Voices**: the natural voices, one download for every language, from GitHub (github.com/amalino-app/voices, or the original sherpa-onnx release if that isn't available). Amalino tells you the size first, and asks before using mobile data.
- **The speech recogniser** for **Listen to what I say**, from GitHub (k2-fsa/sherpa-onnx).
- **Pictures**: if you search all of ARASAAC or other symbol sets online (Global Symbols), only your search words are sent. Pictures you choose are saved on the device.
- **Offline translation**: on Android, Google's ML Kit translation model, once per language. On iPhone and iPad, the languages come from Apple's own Translate settings. No words from the app are sent.

## Features that work on the device

- **Listen to what I say** recognises speech on the device. Audio is never saved or sent.
- **Pages for the moment** uses the time of day only. Amalino doesn't use your location or your calendar.
- **Suggest talking spots** looks at a scene's photo on the device. On Android it uses Google ML Kit: photos never leave the device, but ML Kit sends Google anonymous information about how the feature performs and is used. The same applies to offline translation on Android. iPhone and iPad use Apple Vision, on the device.

## What could leave the device

Apart from the anonymous ML Kit information above, and your internet (IP) address when Amalino downloads something, only what you choose to send:

- a backup file you export and share,
- boards you export to another app,
- a printed or saved PDF.

Features that would need an online service, like **Sync and sharing**, the **Board library** and the cloud helpers, aren't in this version of the app.

## Deleting everything

Uninstalling the app deletes everything it stored on the device. Keep an exported backup if you want to restore later.

The full privacy policy is the website's [privacy page](site:privacy), which also covers the website itself. The app links to it in **About and licences** and at the end of setup.
