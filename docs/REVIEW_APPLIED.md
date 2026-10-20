# Localization review: what was applied

Source: the owner-commissioned native localization review of the local preview of 2026-10-20
(`LOCALIZATION_REVIEW.md`, kept outside this repository). Applied on 2026-10-20 with the owner's decisions of the
same day. This file is not published by the build (`site/build.py` only reads `site/`, `manual/` and
`translations/`).

Owner decisions used:

1. Author gender: the masculine first-person forms stay (ru, uk, es, lt, ar); the gender-neutral rewrites were used
   only where they were better text anyway.
2. Quoted app feature names on the site come from the app's own strings (`{app:key}` in `website.tsv`), after the
   wrong app strings were fixed in the app (see "App strings" below).
3. Form of address on the site and in the app: da du, ru вы (lowercase), uk ви, es tú, lt jūs (lowercase), ar
   generic masculine أنتَ. No capitalised Вы/Jūs was found in the app strings or the website.
4. AAC term on the website only: da ASK, ru АДК (+ «коммуникатор»), uk АДК, ar التواصل المعزز والبديل (AAC),
   es CAA (+ SAAC once), lt «alternatyvioji komunikacija (AAK)» (formal term once on About; a Lithuanian speech
   therapist must still confirm, noted in the app repository's `docs/review/language-audit/lt.md`).
5. Everything else implemented, checked against the current build and app first.
6. The English manual is approved; it is not translated in this task. Only the English source fixes and the
   "(in English)" signposting were done.

Facts settled against the app: the natural voices are one download of **about 129 MB** (the app's real size is
128.8 MB; the review proposed 130, the app shows 129, so the site now says 129 and the speech settings were
changed to round it too); about **200 core words**; about **2,500 words in each language**; ARASAAC downloads its
word list and the chosen pictures, Global Symbols receives the search words.

## App strings (app repository, content/ui/strings.tsv)

| Key | Language | Old | New |
|---|---|---|---|
| aiListen | ru | Слушать собеседника | Слушать, что я говорю |
| aiListen | uk | Слухати співрозмовника | Слухати, що я кажу |
| aiListen | ar | الاستماع إلى المحاور | الاستماع إلى ما أقوله |
| aiListen | es | Escuchar al adulto | Escuchar lo que digo |
| aiListenModelRemoveAsk | ru, uk, ar, es | the old name | «the new name» in quotes |
| aiListenSub | en (+ en-US) | While you switch the microphone on (top bar), … words that could answer | When you turn on the microphone in the top bar, … words the child could use to answer |
| suggestHotspots | da | Foreslå områder | Foreslå områder, der taler |
| suggestHotspots | ru | Предложить точки | Предложить говорящие точки |
| suggestHotspots | uk | Запропонувати точки | Запропонувати точки, що говорять |
| suggestHotspots | es | Sugerir zonas | Sugerir zonas que hablan |
| suggestHotspots | lt | Pasiūlyti kalbančias vietas | Siūlyti kalbančias vietas (every Suggest label now uses Siūlyti) |
| suggestFailed | da, ru, uk, es | … områder / точки / zonas | the same talking-spot term as above |
| syncTitle | ru | Синхронизация и доступ | Синхронизация и общий доступ |
| syncTitle | uk | Синхронізація і доступ | Синхронізація і спільний доступ |

Not changed in the app (noted for the owner): `languagePreviewNote` and `needThisTellUs` say "Tell us" (the review
accepts "us" in app strings; the manual quotes them as they are).

Done later in the app (2026-10-20): `restoreHowTo` now says Grown-up tools → Data → History and backups → Export
backup in all 7 languages; `theme.teen` is "Teen (a more grown-up look)" in English and the same positive wording in
the other 6 languages (drafts for the native check), and the English manual uses it; the Danish 123 keyboard page has
» « in Danish order (» starts a word, « attaches to it) and every keyboard has the straight ", and the keyboard page
of every manual says so.

## Technical items

| # | Item | Status |
|---|---|---|
| T1 | Arabic: whole Latin runs in one isolate | done: `isolate_latin` joins words with "." and "/" and numbers after a Latin word (github.com/amalino-app/voices, iOS 26, Supertonic 3); tests added |
| T2 | Arabic title starts with "Amalino" | done: the build puts U+200F before an Arabic title/description that starts with a Latin letter; the ar text agent also made titles Arabic-first where natural |
| T3 | letter-spacing on Arabic h1 | done: `:lang(ar) h1 { letter-spacing: normal; }` |
| T4 | hreflang, x-default, canonical | already built with an https `--site` (production); the review saw the local preview, whose `--site http://localhost:8765` was rejected. `clean_site` now accepts http://localhost / 127.0.0.1, so the preview has them too (no CNAME there) |
| T5 | og:locale | done: en_GB |
| T6 | non-breaking spaces | done: a typography pass per language in the build (number + MB/GB/МБ/ميغابايت/%/mm, iOS/Android/Supertonic + number, before a spaced dash, after one-letter ru/uk words, lt "t. y.") |
| T7 | robots.txt and sitemap.xml | already built with a site URL (all language pages, pickers and manual pages with alternates); now in the local preview too |
| T8 | "(in English)" on manual links | already in all 6 languages (`nav.manualEn`, nav and footer, with hreflang="en"). Skipped: the localized manual landing pages and the "only in English" banner (the owner decided the manual is not translated in this task). Done later: the manual is translated and each language has its own landing page (manual/<lang>/index.md) |
| T9 | English-only outside links | done: hreflang="en" on the GitHub and Cloudflare privacy links, and "(in English)" after them in each language (`link.inEnglish`) |
| T10 | uk: Ukrainian before Russian in running-text lists | done by the uk text pass where the text lists languages; the language menu keeps the global order |

## English (en)

### Site pages

| Item | Status |
|---|---|
| Home 1 title "talking app (AAC)" | done (adapted: "Amalino: a free talking app (AAC) for children"; the full proposal is 66 characters, over the 60 limit) |
| Home 2-5, 7, 9-11, 14, 16 | kept |
| Home 6 "works without the internet" | done |
| Home 8 words in the same place | done |
| Home 12 platform order | done |
| Home 13 preview + "If you spot a wrong word" | done |
| Home 15 "Do you speak another language?" | done (the review's alternative "Can you help with a language?", which fits both checking and adding) |
| Home 17 the free promise three times | skipped: the build check requires the promise on home and in the footer, and the hero line is the one people see; optional in the review |
| About 3 simply "no" | done |
| About 6 "making", joined sentence | done |
| About 9 "Tested on real devices" | done |
| About 10 "and then native speakers check them" | done |
| About 12 "free for children and families" question | skipped: owner decision (Round 1, 2026-10-06): schools may pay later, so the promise stays as it is |
| About 13 licence names | done (ARASAAC CC BY-NC-SA 4.0, Mulberry Symbols CC BY-SA, OpenMoji CC BY-SA 4.0, "the OpenRAIL-M licence"; Mulberry's version left out until checked) |
| Privacy 3 the list incl. the child's name | done |
| Privacy 4 backups in short sentences | done |
| Privacy 6 pictures: what is sent | done (adapted to the code: ARASAAC's word list and the chosen pictures are downloaded, only the search words are sent) |
| Privacy 7 one download that covers every language | done, with 129 MB (the app's size) |
| Privacy 8 "(not in the app yet)", future tense | done |
| Privacy 10 Pages for the moment | kept (both are app strings) |
| Privacy 11 no "framework" | done |
| Privacy 12 translate paragraph split | done; the UI name is `{app:offlineTranslation|label}` ("Offline translation"), as the app shows it |
| Privacy 16 email | done |
| Translate 2 email | done |
| Translate 3 "needs to be checked" | done |
| Translate 5 preview until checked | done |
| Shared UI: manual index "See how to help" | done in the manual (points to the address in the footer and to a fix on GitHub; no hard-coded address, since the site's address is a build setting) |

### Manual (approved by the owner; English source fixes only)

| Page | Items | Status |
|---|---|---|
| Index | 3 modelling glossed, 4 how to help, 5 test version note; Getting started line without "installing"; Scenes line "talking spots" | done |
| Getting started | 1 meta, 3 "Use Wi-Fi" (129 MB kept), 7 the child's own sentences, 8 "40% done", 10 active voice + quoted UI string, 13 Lock this device to the app = the same instructions as Keep the child in the app (checked in the code) | done |
| Getting started | 6 "Tell us about a wrong word" | kept: exact app string |
| The child's board | 1 ★ Favourites in the alt text, 3 "go back to it", 4 Hold time path and Forms | done |
| Words and folders | 1 about 2,500 in each language, 2 about 200 core words, 4 about 7 mm, 7 shaded dark | done |
| Quick phrases | 2 quotes around "stop" and "help me" (also in Keyboard) | done |
| Keyboard | 2 numbers and punctuation, 3 Activate when the finger lifts, 5 extra suggestion, 6 about 6 mm, 7 quotes | done |
| Keyboard | 2 Danish » « | kept: the app's Danish keyboard offers « »; noted for the owner |
| Scenes | 2 the level example placed in a folder, 3 "talking spot" throughout, 4 "Any other shape", 5 Change crop | done |
| Editing | 3 shaded dark, 5 recording in sentences, 7 Add greyed out, 8 the Languages path (Boards and words) | done |
| Settings | 1 four groups + what "Settings →" means, 2 alt "grown-up settings", 5 graduation-cap icon, 6 "appear on their own board", 7 Hide heading, 10 English spelling, 11 quoted long UI name, 16 Speak each word, 17 Listen to what I say, 19 Diagnostics without "we" | done |
| Settings | 3 Why this matters / Why this helps | kept: two different app strings (`tipTitle`, `mythBuster`) |
| Settings | 13 Teen (no childish look) | done later: the app label is now "Teen (a more grown-up look)" (2026-10-20) |
| Settings | 14 Fitzgerald key gloss | skipped: optional |
| Voices | 2 iOS 17 or later, 4 129 MB (already), 5 voice age, 7 Sam's name, 8 the name | done |
| Sharing and printing | 4 the History and backups path (Data), 5 plainer restore, 8 a word for each print option | done (A4 only: the app has no Letter size) |
| Tips for families | 3, 5, 7, 8 | done |
| Privacy (manual) | 1 "me", 4 the site's ML Kit wording, 5 what can leave the device | done |
| All | "e-mail" -> "email" | done (the manual already said email; the site and build messages now too) |

## da (Danish) - website.tsv

| Item | Key | Status |
|---|---|---|
| Summary: "prøveversion" -> foreløbig | home.preview, about.how3, tr.improveIntro | done |
| Summary: sikkerhedskopi throughout | pr.osBackup | done |
| Summary: billeder (pictograms) vs fotos (photos) | pr.onDevice, pr.camera | done |
| Summary: app feature names | all {app:...} | done (adapted: placeholders kept per owner decision 2; see app-string notes) |
| Summary: ASK spelled out once | home.meta, about.p2 | done |
| Summary: calques list | various | done (see rows below) |
| Home 1 title | home.title | done (adapted: EN title changed; "med billeder" kept, "der ikke taler endnu" dropped to stay short) |
| Home 2 meta | home.meta | done (adapted: ASK spelled out; language list shortened to "dansk og seks andre sprog" to fit 155) |
| Home 3 draft banner | draftBanner | done (adapted: kept "en foreløbig oversættelse", took "gennemlæst") |
| Home 4 H1 | home.h1 | kept |
| Home 5 lead | home.lead | done (adapted: "på jeres eget sprog", "derhjemme" dropped as redundant) |
| Home 6 badge | free | kept |
| Home 7 story | home.story | done (also mirrors EN rewrite) |
| Home 8 link "Læs, hvorfor…" | about.h1 | skipped: the link text is the About H1 key, shared with the page heading |
| Home 9 status | home.status | done |
| Home 10-12 | | kept |
| Home 13 f1 body | home.f1.body | done (+ EN "show more words") |
| Home 14 | | kept |
| Home 15 f2 body | home.f2.body | done |
| Home 16-20 | | kept |
| Home 20 platforms | home.platforms | done (EN order changed: iPhone, iPad og Android-telefoner og -tablets) |
| Home 21 preview + email | home.preview, home.previewEmail | done (+ EN "still") |
| Home 22 myth title | home.mythTitle | done |
| Home 23 myth body | home.mythBody | done |
| Home 24 help title | home.helpTitle | done (adapted: review said keep, but EN changed to "Can you help with a language?" -> "Kan du hjælpe med et sprog?") |
| Home 25 help body | home.helpBody | done (adapted: "derhjemme til daglig") |
| Home 26-27 | | kept |
| About 1, 3 | | kept |
| About 2 meta | about.meta | done |
| About 4 story | about.story | done |
| About 5 p1 | about.p1 | done (+ EN quoted »nej«) |
| About 6 p2 | about.p2 | done |
| About 7 p3 | about.p3 | done (adapted: one sentence with "– for …", mirroring EN rewrite) |
| About 8 p4 | about.p4 | done |
| About 9 | | kept |
| About 10 how1 | about.how1 | done |
| About 11 how2 | about.how2 | done ("Afprøvet i praksis"; EN "Tested on real devices" - "på rigtige enheder" would repeat the last sentence) |
| About 12 how3 | about.how3 | done |
| About 13 how4 | about.how4 | done |
| About 14 how5 | about.how5 | kept (already bold) |
| About 15-17 | | kept |
| About 18 thanks | about.thanks | done (+ EN licence names) |
| About 19 repo "(på engelsk)" | about.repo | done |
| About 20-21 | | kept |
| Privacy 1-3 | | kept |
| Privacy 4 draft | pr.draft | done |
| Privacy 5 intro | pr.intro | done |
| Privacy 6-7 | | kept |
| Privacy 8 onDevice | pr.onDevice | done (+ EN: child's name, new order) |
| Privacy 9 osBackup | pr.osBackup | done (+ EN restructure; no bold lead-in because EN has none) |
| Privacy 10 | | kept |
| Privacy 11 internet | pr.internet | done |
| Privacy 12 dlPictures | pr.dlPictures | done (adapted: EN rewritten - downloads word lists + chosen pictures, sends only search words) |
| Privacy 13 dlVoices | pr.dlVoices | done (129 MB, "som dækker alle sprog"; name kept as {app:aiListen}) |
| Privacy 14 later | pr.later | done (+ EN "not in the app yet", future tense) |
| Privacy 15 dlNote | pr.dlNote | done |
| Privacy 16 context | pr.context | kept |
| Privacy 17 camera | pr.camera | done (adapted: EN rewrite without "framework"; name kept as placeholder) |
| Privacy 18 translate | pr.translate | done (+ EN split) |
| Privacy 19 backup | pr.backup | done |
| Privacy 20 | | kept |
| Privacy 21 cookies | pr.webNoCookies | done |
| Privacy 22 hosts | pr.webHosts | done (adapted: no "(på engelsk)" - the build adds it) |
| Privacy 23-25, 27-28 | | kept |
| Privacy 26 notBody | pr.notBody | done |
| Translate 1-3, 6, 8, 11, 13-16, 19, 22 | | kept |
| Translate 4 intro | tr.intro | done |
| Translate 5 write | tr.write | done |
| Translate 7 improveIntro | tr.improveIntro | done (+ EN rewrite) |
| Translate 9 improve1 | tr.improve1 | done |
| Translate 10 improve2 | tr.improve2 | done (adapted note: "(Kolonnerne har engelske navne i regnearket.)") |
| Translate 12 improveNote | tr.improveNote | done |
| Translate 17 add1 | tr.add1 | done |
| Translate 18 add2 | tr.add2 | done |
| Translate 20 addHonest | tr.addHonest | done |
| Translate 21 addMeanwhile | tr.addMeanwhile | done |
| Translate 23 thanks | tr.thanks | done (adapted: "sige, hvad det gerne vil" - "hvad det mener" shifts the meaning) |
| tr.meta "e-mail" | tr.meta | kept (already "mail") |
| UI 1-4, 6-7, 9-15 | | kept |
| UI 5/13 Vejledning (engelsk) | nav.manualEn | skipped: optional; "(på engelsk)" is the natural form and the header fits |
| UI 8 "Vælg sprog" | lang.label | skipped: the same key is the visible footer title "Sprog" (UI 15 keep) |
| Tech: nbsp, JSON-LD, hreflang | | skipped: done by the build |
| Extra: "app-butikkerne" in support.body | support.body | done (App Store og Google Play, as Home 9) |
| Notes for EN source | | applied where they touch da (129 MB, one download, "skal tjekkes", "it" named) |

# ru: website localization review, applied 2026-10-20

File: translations/ru/website.tsv. 63 keys changed. `build.py --check`: ok; `check_translations.py`: ok.

## Global / summary items
| Item | Status |
|---|---|
| AAC term «альтернативная и дополнительная коммуникация (АДК)» | done: home.meta, about.p2 (first mention on About), pick.meta; «АДК» in home.title, about.title, about.meta |
| «коммуникатор» for search | done: home.title, about.title, pick.title |
| вы lowercase | kept (already correct everywhere) |
| Author gender | kept masculine (owner decision 1): about.story «считал», about.p2 «начал», about.p3 «убеждён», about.p4 «рад». about.contact uses the neutral «я с радостью отвечу» because it is better text |
| Non-breaking spaces | skipped: the build inserts them |
| Feature names | kept as {app:...} placeholders; sentences adjusted around them (pr.camera «Функция «…» анализирует», pr.translate «Если включить «…»») |
| 130 MB | done (adapted: 129 MB, owner decision 5) |

## Home
| # | Status |
|---|---|
| 1 title | done (adapted: «Amalino — бесплатный коммуникатор АДК для неговорящих детей», without brackets to stay within 60 characters) |
| 2 meta | done (adapted: the full proposal is 190 characters; now «Бесплатное приложение альтернативной и дополнительной коммуникации (АДК) для неговорящих детей: нажал на картинку — услышал слово. На семи языках.», 143) |
| 3–7, 9, 12, 13, 15, 17, 18, 23, 25, 27, 28 | kept (✓ keep) |
| 4 draft banner | kept (removing it is the owner's call after the native check) |
| 8 story | done (plus the new English structure «Приложение бесплатное, работает без интернета…»; «нелегко» without «пока», because some children may never speak) |
| 10 App Store / Google Play | done |
| 11 «— я сообщу» | done |
| 14 f1 | done (adapted: «добавляйте новые слова, когда ребёнок подрастёт», which follows the English "as your child grows" rather than "is ready") |
| 16 f2 | done |
| 19 f4 title | done («Без слежки и без интернета») |
| 20 f4 body | done (adapted: «только» added; no quotes around «говорит», because they could read as irony about the child's speech) |
| 21 platforms | done (adapted: new English order «Для iPhone и iPad, а также для телефонов и планшетов на Android.») |
| 22 preview / previewEmail | done (adapted to the new English: «…— пока пробная версия, поэтому отдельные слова ещё могут измениться.» / «Заметили ошибку в слове? Напишите мне на {email}.») |
| 24 myth | done |
| 26 helpBody | done (adapted: «Может быть, это вы? Загляните сюда.» for "If that could be you"); helpTitle follows the new English: «Поможете с языком?» |

## About
| # | Status |
|---|---|
| 1 title | done (adapted: «Почему я делаю Amalino — бесплатный коммуникатор (АДК)», because the proposal was 71 characters) |
| 2 meta | done (adapted: «приложение АДК», because the full term goes over 155 characters) |
| 3, 15, 17, 20 | kept |
| 4 story | kept masculine «Я всегда считал» (owner decision 1) |
| 5 p1 | done |
| 6 p2 | done (adapted: kept the masculine «Когда я начал разбираться в…» instead of «Когда дело дошло до»; adds the full АДК term) |
| 7 p3 | done (adapted: «Я убеждён: свой голос должен быть у каждого, а не только у тех, кому повезло.», masculine kept, calque removed) |
| 8 p4 | done («хоть немного облегчит»); kept «я буду очень рад» (masculine) |
| 9 howTitle | done («Как я делаю Amalino») |
| 10 how1 | done (adapted: «их ещё называют ядерной лексикой» instead of «то, что специалисты называют», because «специалист» is forbidden on public pages) |
| 11 how2 | done (adapted to the new English: «чтобы приложение оставалось быстрым. Ничего не считается готовым, пока не заработает на настоящем устройстве.») |
| 12 how3 | done |
| 13 how4 | done |
| 14 how5 | done |
| 16 freeBody | done («Amalino бесплатен — и таким останется») |
| 18 thanks | done, plus the new English licence names (CC BY-NC-SA 4.0, Mulberry Symbols (CC BY-SA), OpenMoji (CC BY-SA 4.0), «по лицензии OpenRAIL-M»); adapted «Их автор — Серхио Палао, который создал их для ARASAAC», because «создал он их» is awkward |
| 19 repo | done («(пока только на английском)») |
| 21 contact | done («Напишите мне на {email} — я с радостью отвечу.») |

## Privacy
| # | Status |
|---|---|
| 1 title | done (adapted: «Политика конфиденциальности Amalino: без рекламы и слежки», because the proposal was 68 characters) |
| 2–7, 9 (text), 10, 16, 20, 24, 25, 27, 28 | kept |
| 8 onDevice | done, plus the new English (the child's name, list after a colon) |
| 9 osBackup | updated to the new English (Android: not included / not copied; «Кроме того, Amalino каждый день делает свою резервную копию…») |
| 11 internet | done |
| 12 dlPictures | updated to the new English (word lists and chosen pictures downloaded, only the search words sent) |
| 13 dlVoices | done (adapted: placeholder kept, so it shows the app's «Слушать, что я говорю»; «один пакет около 129 МБ сразу для всех языков»; «либо из копии…, либо из исходного релиза»; «где хранятся файлы голосов» dropped, as in the new English) |
| 14 later | done (placeholder, so it shows «Синхронизация и общий доступ»); new English: «(в приложении их пока нет)» and the future «спросит… можно будет» |
| 15 dlNote | done (adapted: «Как и любой сайт, каждый из этих сервисов видит…», which avoids the «сайты… сервисы» mismatch in the proposal) |
| 17 camera | done (adapted: placeholder «Предложить говорящие точки», not «места для слов»; rewritten to the new English without «фреймворк»: «встроенное в систему распознавание изображений Apple (Vision)») |
| 18 translate | done, plus the new English split into shorter sentences |
| 19 backup | done |
| 21 webNoCookies | done |
| 22 webHosts | done (document titles capitalised; no «(на английском)» added by hand, as the brief says) |
| 23 webStats | done |
| 26 notBody | done («Это не медицинское приложение…»; the lawyer may choose the strict 1:1 alternative) |

## Help translate
| # | Status |
|---|---|
| 1 title | done |
| 2, 3, 6, 11, 13, 14, 15 | kept |
| 4 intro | done, plus the new English «должен проверить» (an aim) |
| 5 write | done |
| 7 improveIntro | done, plus the new English ("marks it as a preview until a native speaker has checked it") |
| 8 / 16 stepsLabel | done («Как это работает»; one key for both) |
| 9 improve1 | done |
| 10 improve2 | done (English column names kept) |
| 12 improveNote | done |
| 17–23 add1, add2, add3, addHonest, addMeanwhile, addGithub, thanks | done |

## Shared UI and other keys
| # | Status |
|---|---|
| 1–8, 10–14 | kept |
| 9 aria-label «Язык: русский…» | skipped: lang.label is the same key as the visible footer heading, so this needs a template change in build.py |
| 15 draft banner | kept (the owner removes it after the native check) |
| pick.title / pick.meta | done (not in the review, same AAC fixes: «коммуникатор», full АДК term) |
| tr.meta "email" | kept («электронная почта» already) |
| pr.webEmail | kept («Письма на {email} приходят…») |

## Notes for the English source
1–3 handled by the app-string fix and placeholders. 4 transcreated. 5 owner decided (masculine). 6–9: no change needed in ru. 7 («да» accepted?) is still open for the owner.

# LOG uk (Ukrainian website)

| Item | Result |
|---|---|
| Summary 1 AAC term | done: «альтернативна та додаткова комунікація (АДК)» in home.meta, about.meta, pick.meta, about.p2 (first mention in the About body); titles use «застосунок АДК» |
| Summary 2 calques | done (see the page items) |
| Summary 3 grammar around quoted names | done: pr.osBackup «скористайтеся функцією «{app:exportBackup}»», pr.camera «Функція «{app:suggestHotspots}» …»; placeholders kept |
| Summary 4 feature names | kept (fixed in the app strings today; placeholders render «Синхронізація і спільний доступ», «Слухати, що я кажу», «Запропонувати точки, що говорять») |
| Summary 5 author gender | kept masculine (owner decision 1) |
| Summary 6 / T10 language order | done: Ukrainian before Russian in home.f2.body, about.how3, tr.improveIntro; rest of the order unchanged. pick.meta names only Ukrainian + "ще шістьма" |
| Form of address ви | done: home.meta no longer uses ти |
| Typography: NBSP | skipped: the build inserts them |
| Typography: apostrophe | done: ASCII ' → ʼ (U+02BC) in all website keys (the app still uses ASCII ') |
| Home 1 title | done (adapted): «Amalino — безкоштовний застосунок АДК, що говорить за дитину» follows the new English "a free talking app (AAC)"; the review's text was over 60 characters |
| Home 2 meta | done (adapted): spelled-out term, ви register; the language list does not fit in 155 characters (pick.meta keeps the languages) |
| Home 3 skip link | done: «Перейти до основного вмісту» |
| Home 4 nav manual | done (adapted): «Інструкція (англійською)», because one key (nav.manualEn) serves the header and the footer; also nav.manual, man.suffix, man.navLabel → інструкція |
| Home 5 draft banner | done: «Це попередній переклад — …» |
| Home 6–8, 13, 14, 16, 18–22, 24, 27–29 | kept (✓ keep); home.platforms rewritten for the new English order «Для iPhone, iPad, а також для телефонів і планшетів на Android.» |
| Home 9 story | done (adapted): the review's text merged with the new English ("free, works without the internet"): one sentence instead of the separate «І працює без інтернету.» |
| Home 10 link "Чому я створюю Amalino" | done (comes from about.h1) |
| Home 11 status | done |
| Home 12 statusEmail | done |
| Home 15 f1.body | done (+ "нові слова" from the new English) |
| Home 17 f2.body | done (adapted): Ukrainian before Russian, not first (team lead's T10 rule) |
| Home 23 preview | done (adapted): «поки що позначені як пробна версія, тож деякі слова ще можуть змінитися» matches the app label «Пробна версія» and the new English; previewEmail «Якщо помітите неправильне слово, напишіть мені: {email}.» |
| Home 25 mythBody | done |
| Home 26 helpTitle | done (adapted): English is now "Can you help with a language?" → «Допоможете перевірити мову?» |
| About 1 title | done (adapted): «Чому я створюю Amalino — безкоштовний застосунок АДК»; "для дітей" would make 62 > 60 characters |
| About 2 meta | done (adapted): term spelled out; "Для дітей і родин — завжди безкоштовно" dropped for the 155 limit (the sentence already says безкоштовний) |
| About 3 H1 | done |
| About 4 story | done |
| About 5 p1 | done (+ new English «чи просто «ні»») |
| About 6 p2 | done (AAC spelled out at first mention instead of plain «АДК») |
| About 7 p3 | done (follows the new English "because …") |
| About 8 p4 | done |
| About 9 howTitle | done |
| About 10 how1 | done |
| About 11 how2 | done; heading now «Перевіряю на справжніх пристроях.» (new English "Tested on real devices") |
| About 12 how3 | done (adapted): Ukrainian before Russian, not first; app label «пробна версія» kept |
| About 13, 15, 16, 20, 21 | kept |
| About 14 how5 | done |
| About 17 thanksTitle | done: «Подяки» |
| About 18 thanks | done: new licence names (CC BY-NC-SA 4.0, Mulberry Symbols (CC BY-SA), OpenMoji (CC BY-SA 4.0), ліцензія OpenRAIL-M), «(Іспанія)» added; kept the «їх створив» sentence shape |
| About 19 repo | done: «інструкцію користувача» |
| Privacy 1 title | done |
| Privacy 2 meta | done |
| Privacy 3, 6, 7, 10, 20, 23, 24, 26–28 | kept |
| Privacy 4 draft | done |
| Privacy 5 intro | done |
| Privacy 8 onDevice | done (adapted): new English list incl. the child's name; «Усі дані застосунку зберігаються…» |
| Privacy 9 osBackup | done: grammar fixed with «функцією», new English (daily backup by Amalino) |
| Privacy 11 internet | done |
| Privacy 12 dlPictures | done (adapted): new English (downloads word lists and chosen pictures, sends only search words) |
| Privacy 13 dlVoices | done (adapted): 129 MB, one download covering every language, «або з власної копії Amalino …, або з оригінального випуску від розробників»; name via {app:aiListen} |
| Privacy 14 later | done (adapted): «(у застосунку їх ще немає)», future tense «можна буде вимкнути» |
| Privacy 15 dlNote | done |
| Privacy 16 context | done |
| Privacy 17 camera | done (adapted): rewritten from the new English («вбудоване розпізнавання зображень Apple (Vision)», no "фреймворк"); name via {app:suggestHotspots} |
| Privacy 18 translate | done (adapted): split per new English; Apple app «Переклад» (the app's own string says Параметри > Програми > Переклад), «у параметрах програми Apple «Переклад»» |
| Privacy 19 backup | done |
| Privacy 21 webNoCookies | done (apostrophe only) |
| Privacy 22 webHosts | done (adapted): «надходить», «IP-адресу»; document names left lowercase and descriptive because these policies have no official Ukrainian titles |
| Privacy 25 notTitle | done: «Чого Amalino не робить» |
| Translate 1 title | done |
| Translate 2, 3, 5, 8–11, 14–16, 19, 21 | kept |
| Translate 4 intro | done (+ new English "needs to be checked": «має перевірити») |
| Translate 6 improveTitle | done |
| Translate 7 improveIntro | done (adapted): Ukrainian before Russian; new English "marked as a preview until a native speaker has checked it" |
| Translate 12 improveNote | done |
| Translate 13 improveGithub | done (link text «переклад можна виправити й там») |
| Translate 17 add1 | done |
| Translate 18 add2 | done |
| Translate 20 addHonest | done |
| Translate 22 addGithub | done |
| Translate 23 thanks | done |
| Shared 1, 3–5, 7, 8, 10–12, 15, 16 | kept |
| Shared 2 skip | done |
| Shared 6, 13 manual | done (adapted): one key, «Інструкція (англійською)» |
| Shared 9 lang.label «Вибір мови» | skipped: the same key is also the visible footer heading, which the review keeps as «Мова» |
| Shared 14 footer.repo | done: «Сайт, інструкція і переклади — на GitHub» |
| Notes for the English source | applied where they touch uk text (privilege sentence, original release, sync); the "Write to me" variation was already varied (Пишіть / Напишіть мені) |
| English updates (en_website.diff) | mirrored: home.title, home.story, home.f1.body, home.platforms, home.preview, home.previewEmail, home.helpTitle, about.p1, about.p3, about.how2, about.how3, about.thanks, tr.intro, tr.improveIntro, pr.onDevice, pr.osBackup, pr.dlPictures, pr.dlVoices, pr.later, pr.camera, pr.translate; tr.meta/pr.webEmail already said «електронна пошта» / «Листи» |
| pick.title / pick.meta | done: term fixed (АДК as a product removed); these uk keys are not used by the build today (pickers use en) |

Keys changed: 67 (65 rewritten + 2 apostrophe-only: pr.notBody, pr.webNoCookies).

# LOG: ar (Arabic) website

| Item | Status |
|---|---|
| Summary: RTL split isolates (URL, iOS 26, Supertonic 3) | skipped: done in the build (T1, another agent). No bidi marks added. Rendered URL is now one isolate |
| Summary: titles/meta starting with "Amalino" (T2) | done: home.title, home.meta, pick.title, pick.meta now start with Arabic words |
| Summary: AAC term consistent | done: التواصل المعزز والبديل everywhere (home.title/meta, pick.*, about.title/meta/p2); (AAC) in home/pick title or meta and first mention on About (p2) |
| Summary: «مساهمة في مشكلة» | done (about.p4 «في مواجهة مشكلة») |
| Summary: «أرسل إليك» | done (tr.improve1, tr.add1 «سأرسل إليك») |
| Summary: «مساعدات» vs «مساعدون» | done (pr.later «مساعدات») |
| Summary: app feature names | done: all stay {app:...}; current app values checked in context (aiListen is now «الاستماع إلى ما أقوله») |
| Summary: letter-spacing CSS (T3) | skipped: CSS/build, not website.tsv |
| Form of address أنتَ | kept (already generic masculine throughout) |
| Numerals Western, units full word | kept; 130 -> 129 per owner fact |
| No-break spaces | skipped: build inserts them |
| Brand transliteration أمالينو | done (home.meta, about.meta) |
| Home 1 title | done (adapted: AAC term + (AAC) per owner decision 4 and the new English title, instead of «التواصل بالصور») |
| Home 2 meta | done (second, Arabic-first version) |
| Home 3 skip link | done («الانتقال إلى المحتوى») |
| Home 4-7, 9, 12, 15, 20, 25, 27 | kept (review ✓) |
| Home 8 story | done (adapted: also English update "It's free, it works without the internet") |
| Home 10 status | done |
| Home 11 statusEmail | done |
| Home 13 f1.title | done |
| Home 14 f1.body | done (+ "more words" from English update) |
| Home 16 f2.body | done |
| Home 17 f3.title tanween | kept (optional) |
| Home 18 f3.body | done |
| Home 19 f4.title | done (adapted: «خصوصيتك محفوظة، ولا حاجة إلى الإنترنت»; the proposed «…، ودون إنترنت» reads as a fragment) |
| Home 21 platforms | done (adapted: reordered to iPhone, iPad, Android per English update) |
| Home 22 preview/previewEmail | done |
| Home 23 mythTitle | done |
| Home 24 mythBody | done |
| Home helpTitle (English update) | done («هل يمكنك أن تساعد في إحدى اللغات؟») |
| Home 26 helpBody | done |
| About 1 title | done (adapted: dropped «للأطفال» to stay within 60 characters) |
| About 2 meta | done |
| About 3, 10, 13, 15, 16, 19, 20 | kept (review ✓) |
| About 4 story | done |
| About 5 p1 | done (adapted: «يمزحوا» instead of «يُطلقوا نكتة», simpler) |
| About 6 p2 | done (+ (AAC) at first mention) |
| About 7 p3 | done (+ English update structure) |
| About 8 p4 | done |
| About 9 howTitle | done |
| About 11 how2 | done (adapted: English is now "Tested on real devices" -> «أجرّبه على أجهزة حقيقية»; «وعلى» repeated as proposed) |
| About 12 how3 | done |
| About 14 how5 | done |
| About 17 thanksTitle | done («شكر وتقدير») |
| About 18 thanks | done (+ licence names from English update; «ولكل واحد من أهل اللغة» for consistency with «أهل اللغة») |
| About 21 contact | done |
| Privacy 1-4, 6, 7, 10, 11, 16, 20, 21, 23-25, 27, 28 | kept (review ✓) |
| Privacy 5 intro | done |
| Privacy 8 onDevice | done (+ child's name, reordered per English update) |
| Privacy 9 osBackup | done (+ English update: "Amalino also makes a backup every day") |
| Privacy 12 dlPictures | done (adapted: rewritten per English update: word lists + chosen pictures downloaded, only search words sent) |
| Privacy 13 dlVoices | done (adapted: 129 MB «يشمل كل اللغات», "either ... or from the original release", dropped "where the voice files are kept" as in English; {app:aiListen} kept; bidi left to build) |
| Privacy 14 later | done (adapted: "(not in the app yet)" + future tense from English) |
| Privacy 15 dlNote | done |
| Privacy 17 camera | done (adapted: rewritten per new English, no "framework": «تقنية التعرّف على الصور المدمجة من Apple (Vision)», «بيانات مجهولة الهوية») |
| Privacy 18 translate | done (adapted: split per English update; «تُعِدّ» vocalised; «بنظام iOS 26»; «إعدادات تطبيق «ترجمة» من Apple») |
| Privacy 19 backup | done |
| Privacy 22 webHosts | done (adapted: no «(بالإنجليزية)», the build adds it) |
| Privacy 26 notBody | done («حالة صحية») |
| Translate 1-3, 6, 8, 10-12, 14-16, 18, 19, 22, 23 | kept (review ✓; tr.meta "email" already «بريد إلكتروني») |
| Translate 4 intro | done (adapted: English now "needs to be checked" -> «ينبغي أن يراجع») |
| Translate 5 write | done |
| Translate 7 improveIntro | done (adapted: review ✓, but English update changed the structure) |
| Translate 9 improve1 | done |
| Translate 13 improveGithub | done |
| Translate 17 add1 | done |
| Translate 20 addHonest | done |
| Translate 21 addMeanwhile | done (adapted: «بأصوات أفرادها» instead of «بأصواتها») |
| Shared 1 skip | done |
| Shared 2-7, 9-14 | kept (review ✓) |
| Shared 8 lang.label «اختيار اللغة» | skipped: the same key is the visible footer heading, which the review says to keep as «اللغة» |
| Technical checklist 1, 3, 4, 5 | skipped: build/CSS |
| Technical checklist 2 | done (see T2) |
| Notes for the English source | apply to English; the Arabic now follows the updated English (I'll send, not yet available, helpers = مساعدات) |

# LOG: Spanish (es) website

60 keys changed in translations/es/website.tsv. `build.py --check` ok, `check_translations.py` ok.

## Summary-level / systemic
| Item | Result |
|---|---|
| About title "Por qué creo Amalino" | done (now "Por qué estoy creando Amalino, app de CAA gratis para niños", 59 chars, same as the H1) |
| Author gender (yo mismo, sincero) | done (adapted: owner decision 1 keeps the masculine forms; "yo mismo" went anyway because the English lead-in is now "Tested on real devices"; "Te seré sincero" stays) |
| Spain-only words (móvil, ordenador, la web, "ha entrado") | done (teléfono, Mac o PC, el sitio web, "quién visita el sitio") |
| "analíticas" false friend | done (estadísticas de uso, in about.how4 and pr.noAds; "scripts de analítica" kept as the review says) |
| Straight quotes -> « » | done (no straight quotes left in the file) |
| Non-breaking spaces | skipped: the build adds them |
| Feature names checked against the app | done (all {app:…} placeholders kept; app values now «Escuchar lo que digo», «Sugerir zonas que hablan»; wording around them fixed) |
| tú form | kept (already consistent; no usted found) |
| AAC term CAA, SAAC once | done (spelled out in home.meta, pick.meta and on About in about.p2; SAAC once in about.meta: "app gratuita de CAA (en España, SAAC)") |
| Inclusive language: doubled form once per page | done (H1 "niños y niñas", home.f1 "tu hijo o hija", about.p4, pr.meta, pr.onDevice, tr.intro, tr.thanks) |
| og:locale es_ES | skipped: build setting, not website.tsv (the review says es_ES is acceptable) |

## Home
| # | Result |
|---|---|
| 1 title | done (adapted: the review's version was 70 chars, so it is now "Amalino: app de CAA gratis con pictogramas para niños", 53 chars; keeps CAA, gratis and pictogramas) |
| 2 meta | done (adapted: the full term "comunicación aumentativa y alternativa (CAA)" is in, but listing all 7 languages goes past 155 chars, so it says "En español y 6 idiomas más"; 155 chars) |
| 3 skip link | done ("Ir al contenido principal") |
| 4, 5, 6 | kept |
| 7 H1 | done |
| 8 lead | done (adapted: "Basta con tocar un pictograma para que el dispositivo diga la palabra en voz alta, en el idioma de la familia"; "el dispositivo" instead of "el teléfono" because tablets are included too, and no second doubled form right after the H1) |
| 9 | kept |
| 10 story | done, and mirrored the new English ("Es gratis, funciona sin internet y habla por ellos…") |
| 11–15 | kept |
| 16 f1.body | done (adapted: "ve mostrando más palabras", not "añadiendo", because hidden buttons are shown and nothing moves, as in the new English "show more words") |
| 17 | kept |
| 18 f2.body | done |
| 19 f3.title | done ("Ayuda para los adultos") |
| 20 f3.body | done |
| 21 | kept |
| 22 f4.body doubling | skipped: optional, and the page already uses the doubled form in f1 |
| 23 platforms | done (adapted to the new English order: "Para iPhone y iPad, y para teléfonos y tabletas Android.") |
| 24 preview + email | done (mirrored the new English: "están todavía en versión de prueba, así que algunas palabras pueden cambiar"; "Si ves una palabra que no está bien, escríbeme a {email}.") |
| 25 mythTitle | done |
| 26 mythBody | done (adapted: « », "no hace falta que…"; the bridge idiom is now "Es un apoyo en el camino hacia el habla", not a literal "puente") |
| 27 helpTitle | done (adapted: the English changed to "Can you help with a language?", so "¿Me ayudas con un idioma?") |
| 28 helpBody | done ("¿Te animas? Aquí te cuento cómo.") |
| 29, 30 | kept |

## About
| # | Result |
|---|---|
| 1 title | done (adapted: the proposed text is 63 chars, so "una" was dropped: 59 chars) |
| 2 meta | done (adapted: "una sola persona crea una app gratuita de CAA (en España, SAAC) que da palabras a los niños en los idiomas de su familia"; the full CAA term moved to about.p2 because of the 155-char limit) |
| 3 | kept |
| 4 story | done |
| 5 p1 | done (adapted: "o, sencillamente, «no»", which mirrors the new English quotes; "pedir de beber" kept because it is natural in every region) |
| 6 p2 | done (+ "CAA (comunicación aumentativa y alternativa)" spelled out at the first mention on the page) |
| 7 p3 | done (mirrored the new English: "…que funciona sin internet, porque tener voz no debería ser un privilegio") |
| 8 p4 | done |
| 9 | kept |
| 10 how1 | done (vocabulario núcleo; about 200) |
| 11 how2 | done ("Probado en dispositivos reales", which matches the new English) |
| 12 how3 | done (adapted: "con un traductor automático de IA, y después los revisan hablantes nativos"; the second sentence kept with "Mientras…no haya revisado") |
| 13 how4 | done |
| 14 how5 | done (adapted: "(es lo que se llama modelado)"; the review's "los terapeutas" is a forbidden word) |
| 15–17 | kept |
| 18 thanks | done (ARASAAC's own Spanish attribution + the new licence names: CC BY-NC-SA 4.0, Mulberry Symbols (CC BY-SA), OpenMoji (CC BY-SA 4.0), "la licencia OpenRAIL-M") |
| 19 repo | done ("El sitio web, el manual de uso (en inglés)…") |
| 20, 21 | kept |

## Privacy
| # | Result |
|---|---|
| 1 title | kept |
| 2 meta | done |
| 3 | kept |
| 4 draft doubling | skipped: optional |
| 5 intro | done |
| 6, 7 | kept |
| 8 onDevice | done (+ the child's name, as in the new English) |
| 9 osBackup | done (Mac o PC, teléfono, « »; mirrored the new English "Amalino también hace una copia cada día…"; the button name stays {app:exportBackup} = «Exportar copia», see the app-string note) |
| 10 noAds | done |
| 11 internet | done |
| 12 dlPictures | done (« », pictogramas; mirrored the new English: downloads word lists and the pictures you choose, sends only search words) |
| 13 dlVoices | done (129 MB that covers every language, "ya sea de la copia propia… o de la publicación original", "Amalino solo los descarga"; aiListen is now «Escuchar lo que digo» in the app) |
| 14 later | done (« », "(todavía no están en la app)", future tense, "cuando quieras"; the name stays {app:syncTitle}) |
| 15 dlNote | done ("dirección IP", "servicios") |
| 16 context | done ("a la hora de comer", colon) |
| 17 camera | done (rewritten from the new English, without "framework": "el reconocimiento de imágenes integrado de Apple (Vision)"; the name is now «Sugerir zonas que hablan» in the app) |
| 18 translate | done (split as in the new English; « », "se configura una vez para cada idioma", "aunque" sense in its own sentence) |
| 19 backup | done (two sentences; the name stays {app:exportBackup}) |
| 20, 21 | kept |
| 22 webHosts | done ("dirección IP"); the Spanish GitHub link was skipped: the URL is fixed in site/build.py OUTSIDE_LINKS |
| 23 webStats | done |
| 24, 25 | kept |
| 26 notBody | done (adapted: "a los niños" instead of doubling; "no hace seguimiento ni trata ninguna enfermedad ni trastorno") |
| 27, 28 | kept |

## Help translate
| # | Result |
|---|---|
| 1–3 | kept |
| 4 intro | done (mirrored the new English "needs to be checked": "tiene que revisarla alguien que hable ese idioma") |
| 5, 6 | kept |
| 7 improveIntro | done (split as in the new English; «versión de prueba» matches the app's languagePreview) |
| 8 | kept |
| 9 improve1 | done (adapted: "Cada fila tiene…", because the review's "En cada fila hay el texto" is ungrammatical) |
| 10 improve2 | done (« ») |
| 11 | kept |
| 12 improveNote | done |
| 13 improveGithub | done ("también") |
| 14–16 | kept |
| 17 add1 doubling | skipped: optional; the page already doubles in the intro and the closing line |
| 18 | kept |
| 19 add3 | done |
| 20 addHonest | done (adapted: "Te seré sincero" kept by owner decision 1; only the comma fix) |
| 21, 22 | kept |
| 23 thanks | done |

## Shared UI
| # | Result |
|---|---|
| 1 skip | done |
| 2, 3 | kept |
| 4 nav.about | done ("Sobre Amalino") |
| 5–7 | kept |
| 8 lang.label "Cambiar idioma" | skipped: the same key is also the visible footer heading "Idioma", which the review (#15) says to keep |
| 9–13 | kept |
| 14 footer.repo | done ("El sitio web, …") |
| 15, 16 | kept |
| JSON-LD description | done via home.meta (the build reuses it) |
| pick.meta | done (not in the review: the full AAC term, 151 chars) |

## Notes for the English source
1–11: these are for English or the owner. No Spanish change is needed beyond the above. #2, #3 and #6 are settled by the new app strings and the 129 MB wording.

## Lithuanian (lt): website review applied (translations/lt/website.tsv)

Keys changed: 81. Build `--check` and `check_translations.py` both pass.

### Global
| Item | Status |
|---|---|
| Author gender (tikėdamas, padedamas) | done (adapted): owner keeps masculine forms; the two neutral rewrites (about.p3 "nes tikiu", about.how3 "juodraščius parengia DI vertimas") are used because they read better and follow the new English |
| AAC term | done: «alternatyvioji komunikacija (AAK)» in home.title; spelled out at first mention in home.meta, about.meta, about.p2 (pick.meta already had it). Formal «augmentinė ir alternatyvioji komunikacija» not used (optional "at most once"; no natural spot in About without naming professionals, which the forbidden-word list bars) |
| jūs lowercase | kept (already consistent) |
| „…“ quotes around {app:…} | kept; every {app:…} placeholder unchanged; generic noun *funkcija* added before quoted names where a case was needed |
| reklama singular site-wide | done (home.f4, about.how4, about.freeBody, pr.noAds, pr.title, pr.meta) |
| skaičiuoklė -> lentelė | done (tr.meta, tr.intro, tr.improve1/3, tr.add1) |
| Brand names + generic noun (GitHub platformoje, iPad planšetėje, bendrovei Google, iPhone ir iPad įrenginiuose) | done |
| NBSP | skipped: the build inserts it |
| Siūlyti vs Pasiūlyti | done via app (both now Siūlyti; site uses placeholders) |

### Home
| # | Status |
|---|---|
| 1 title | done (adapted): English title changed to "a free talking app (AAC)"; now "Amalino: nemokama alternatyvioji komunikacija (AAK) vaikams" (59 chars) |
| 2 meta | done (adapted): proposal is 176 chars; shortened to 144, language list replaced by "jūsų šeimos kalba" |
| 3 skip | kept |
| 4 draft banner | done (text); removing the banner is the owner's call |
| 5 H1 | done |
| 6 lead | done |
| 7 tagline | kept |
| 8 story | done (adapted to new English "It's free, it works without the internet…") |
| 9 link | kept |
| 10 status | done |
| 11 statusEmail | done |
| 12 featuresTitle | done |
| 13 f1.title | done |
| 14 f1.body | done ("show more words" matches the new English) |
| 15 f2.title | kept |
| 16 f2.body | done |
| 17 f3.title | kept |
| 18 f3.body | done |
| 19 f4.title | kept |
| 20 f4.body | done |
| 21 platforms | done (adapted: new English order iPhone, iPad, Android) |
| 22 preview / previewEmail | done (adapted to the new English split sentences) |
| 23 mythTitle | kept |
| 24 mythBody | done (adapted: "bridge to talking" as "Paveikslėliai padeda prabilti, o ne atstoja kalbą" instead of the literal "tiltas į kalbą", where *kalba* is ambiguous language/speech) |
| 25 helpTitle | done (adapted: new English "Can you help with a language?" -> "Gal galite prisidėti prie vertimo?") |
| 26 helpBody | done (adapted: "Gal galėtumėte tai padaryti jūs? Pažiūrėkite, kaip tai vyksta.") |
| 27 helpLink | kept |
| 28 footer | see Shared UI |

### About
| # | Status |
|---|---|
| 1 title | kept (with "AAK"; the spelled-out term does not fit in 60 chars; meta and p2 expand it) |
| 2 meta | done (adapted: tagline sentence dropped to stay at 146 chars) |
| 3 H1 | kept |
| 4 story | done |
| 5 p1 | done (comma before *ar* removed, "pasakyti, kas skauda") |
| 6 p2 | done (adapted: kept "pasikliauti kalbėjimu" instead of "kalba", which could read as "language") |
| 7 p3 | done (one sentence, following the new English) |
| 8 p4 | done |
| 9 howTitle | done |
| 10 how1 | done |
| 11 how2 | done ("Išbandyta tikruose įrenginiuose", matches new English) |
| 12 how3 | done (adapted: "bandomoji versija" without quotes, since it is not a placeholder and app names are never hand-typed in quotes) |
| 13 how4 | done |
| 14 how5 | done |
| 15 freeTitle | kept |
| 16 freeBody | done |
| 17 thanksTitle | done (Padėkos) |
| 18 thanks | done (adapted: new licence names CC BY-NC-SA 4.0, Mulberry Symbols (CC BY-SA), OpenMoji (CC BY-SA 4.0), "pagal OpenRAIL-M licenciją"; last clause "visiems tėvams bei gimtakalbiams, kurie…" to fix agreement) |
| 19 repo | done |
| 20 contactTitle | kept |
| 21 contact | done |

### Privacy
| # | Status |
|---|---|
| 1 title | done |
| 2 meta | done |
| 3 H1 | kept (Privatumas; "Privatumo politika" left to the owner, see Notes 9) |
| 4 draft | done |
| 5 intro | done |
| 6 appTitle | kept |
| 7 noAccount | kept |
| 8 onDevice | done (adapted: new English adds the child's name) |
| 9 osBackup | done (adapted: new English "Amalino also makes a backup every day…") |
| 10 noAds | done |
| 11 internet | done (papildoma -> pasirenkama) |
| 12 dlPictures | done (adapted: new English, word lists + chosen pictures downloaded, only search words sent) |
| 13 dlVoices | done (adapted: keeps "GitHub (github.com)" for the build check; 129 MB, one download that covers every language, "kalbos atpažinimo modelis", either own copy or original release) |
| 14 later | done (adapted: "(programėlėje jų dar nėra)", future tense) |
| 15 dlNote | done |
| 16 context | done |
| 17 camera | done (adapted: rewritten after the new English, "integruotas Apple vaizdų atpažinimas (Vision)", "Šio siuntimo išjungti negalima") |
| 18 translate | done (adapted: split like the new English; "įjungti kalbų nustatymuose" avoids the tautology; Apple's Translate left unquoted as in the app) |
| 19 backup | done |
| 20 webTitle | kept |
| 21 webNoCookies | done |
| 22 webHosts | done (link texts in locative; no "(in English)" added) |
| 23 webStats | done |
| 24 webEmail | done |
| 25 notTitle | done (Ko Amalino nedaro) |
| 26 notBody | done |
| 27 contactTitle | kept |
| 28 contact | done |

### Help translate
| # | Status |
|---|---|
| 1 title | kept |
| 2 meta | done |
| 3 H1 | kept |
| 4 intro | done ("turi patikrinti", matches new English "needs to be checked") |
| 5 write | kept |
| 6 improveTitle | done |
| 7 improveIntro | done (adapted: new English "marks it as a preview until a native speaker has checked it"; label unquoted) |
| 8 stepsLabel | kept |
| 9 improve1 | done |
| 10 improve2 | done |
| 11 improve3 | done |
| 12 improveNote | done (sąranka matches the app) |
| 13 improveGithub | done |
| 14 addTitle | kept |
| 15 addIntro | done |
| 16 add1 | done |
| 17 add2 | done |
| 18 add3 | done |
| 19 addHonest | done |
| 20 addMeanwhile | kept |
| 21 addGithub | done (link text "pradėti naują kalbą") |
| 22 thanks | done |

### Shared UI
| # | Status |
|---|---|
| U1–U3 | kept |
| U4 nav.about | done (Apie projektą) |
| U5/U14 nav.manualEn | done (Naudotojo vadovas (anglų k.)); nav.manual also "Naudotojo vadovas" |
| U6, U7 | kept |
| U8/U9/U10 language labels | skipped: one key (lang.label) feeds the summary aria-label, the footer nav aria-label and the visible heading in site/templates/layout.html; separate labels need a template change, outside this task |
| U11, U12 | kept |
| U13 footer.contact | done ("Rašykite man adresu {email}", no final period) |
| U15 footer.repo | done |
| U16 banner | see Home 4 |

### Notes for the English source
| # | Status |
|---|---|
| 1 130 MB ambiguity | done (129 MB, "tinkantis visoms kalboms") |
| 2 Suggest… names | done in the app (Siūlyti); "kalbančios vietos" left as the app has it |
| 3 original release | kept as English ("pirminio jų leidimo") |
| 4 can't be turned off | done ("Šio siuntimo išjungti negalima") |
| 5 ten voices | kept ("Visomis šiomis kalbomis kalba dešimt natūralių balsų") |
| 6 author gender | owner decided: masculine |
| 7 "ready" | done ("nereikia laukti, kol vaikas bus „pasiruošęs“") |
| 8 column names | done (kept English, glossed "Correction" once) |
| 9 Privacy vs policy | skipped: owner decision |

## After the agents' passes

- `about.meta` in uk, es and lt was shortened by hand so it still ends with the free promise (`freeTitle`, a build
  test) and stays within 155 characters.
- `link.inEnglish` added in all 7 languages (the "(in English)" label after English-only outside links; not shown
  on English pages).

## Suggested order for translating the manual later (from the review)

1. Tips for families; 2. Getting started; 3. The child's board; 4. Privacy (or merge into the site's privacy
page); 5. Words and folders, Editing and moving buttons; 6. Quick phrases, Voices, Sharing and printing, Scenes,
Keyboard; 7. last, Settings, screen by screen (wait until the app's own strings are checked). Translators copy UI
names from the app's translation files, never translate them afresh. Also suggested: a short localized
`/<lang>/manual/` landing page and an "only in English for now" banner on English manual pages.

Done since: the manual is translated into all 6 languages (drafts for the native check, a draft note on each page
until `manual:<page>` is in reviewed.txt), and each language has its own `/<lang>/manual/` landing page
(manual/<lang>/index.md), so the English-only banner isn't needed.
