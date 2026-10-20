<!-- description: Hvad Amalino gemmer på enheden, hvad appen henter og hvornår, og hvad der eventuelt forlader enheden. Ingen reklamer, ingen sporing, ingen konto. -->
# Privatliv

Amalino er lavet, så barnets ord bliver hos barnet. Der er ingen reklamer, ingen sporing og ingen konto.

## Det bliver på enheden

- Barnets tavler, ord, fotos og optagelser.
- Det, barnet siger, og de brugsdata, der ligger bag **{app:progress}** og oversigten **{app:thisWeek}**.
- Barnets navn.

Det hele gemmes kun på enheden, og det er krypteret. Intet af det bliver sendt til mig.

## Sikkerhedskopier

- **Den automatiske daglige sikkerhedskopi** bliver på enheden og kan kun åbnes dér.
- **{app:exportBackup}** laver en fil, der er beskyttet med din adgangskode, så du kan flytte den til en ny enhed. Du bestemmer selv, hvor du gemmer den.
- **iPhone og iPad**: Sikkerhedskopierer du enheden til iCloud eller en computer, kommer Amalinos data med i sikkerhedskopien.
- **Android**: Amalinos data kommer ikke med i din Google-sikkerhedskopi og bliver heller ikke kopieret over på en ny telefon.

Læs mere under [Deling og udskrift](sharing-and-printing.md).

## Det henter Amalino

Nogle ting hentes én gang, når du beder om dem, og virker derefter offline. Der sendes intet om barnet.

- **Stemmer**: de naturlige stemmer, én samlet download til alle sprog, fra GitHub (github.com/amalino-app/voices eller den oprindelige udgivelse af sherpa-onnx, hvis den første ikke er tilgængelig). Amalino fortæller dig først, hvor stor filen er, og spørger, før der bruges mobildata.
- **Talegenkendelsen** til **{app:aiListen}**, fra GitHub (k2-fsa/sherpa-onnx).
- **Billeder**: Søger du i hele ARASAAC eller i andre symbolsæt online (Global Symbols), sendes kun de ord, du søger efter. De billeder, du vælger, gemmes på enheden.
- **{app:offlineTranslation|label}**: På Android hentes Googles ML Kit-oversættelsesmodel én gang for hvert sprog. På iPhone og iPad kommer sprogene fra Apples egne indstillinger for Oversæt. Der sendes ingen ord fra appen.

## Funktioner, der kører på enheden

- **{app:aiListen}** genkender tale på enheden. Lyden bliver aldrig gemt eller sendt.
- **{app:contextBoards}** bruger kun klokkeslættet. Amalino bruger hverken din placering eller din kalender.
- **{app:suggestHotspots}** ser på fotoet i en scene på enheden. På Android bruges Google ML Kit: Fotoet forlader aldrig enheden, men ML Kit sender anonyme oplysninger til Google om, hvordan funktionen kører og bliver brugt. Det samme gælder offline-oversættelse på Android. På iPhone og iPad bruges Apple Vision på enheden.

## Det kan forlade enheden

Bortset fra de anonyme ML Kit-oplysninger ovenfor og din internetadresse (IP-adresse), når Amalino henter noget, er det kun det, du selv vælger at sende:

- en sikkerhedskopi, du eksporterer og deler,
- tavler, du eksporterer til en anden app,
- en udskrevet eller gemt PDF.

Funktioner, der ville kræve en onlinetjeneste – som **{app:syncTitle}**, **{app:library}** og hjælperne i skyen – findes ikke i denne version af appen.

## Slet alt

Når du afinstallerer appen, slettes alt, hvad den har gemt på enheden. Gem en eksporteret sikkerhedskopi, hvis du vil kunne gendanne senere.

Den fulde privatlivspolitik står på hjemmesidens [side om privatliv](site:privacy), som også handler om selve hjemmesiden. Appen linker til den under **{app:about}** og til sidst i opsætningen.
