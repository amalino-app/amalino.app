<!-- description: Kaip sukurti sceną Amalino programėlėje: nufotografuokite, apkarpykite, pasirinkite mygtuko vietą ir nubrėžkite kalbančias vietas. -->
# Scenos

**Scena** – tai nuotrauka su kalbančiomis vietomis, t. y. sritimis, kurios prabyla, kai vaikas jas bakstelėja: žaidimų aikštelė su sūpynėmis ir čiuožyne, virtuvės stalas, močiutės sodas. Vaikas bakstelėja sūpynes ir išgirsta „sūpynės“. Scenos puikiai tinka mažiems vaikams ir kalbėti apie tikras vietas bei akimirkas.

## Kaip sukurti naują sceną

1. Atidarykite suaugusiųjų nustatymus ir pasirinkite **{app:editBoard}**.
2. Po viršutine juosta esančios eilutės **{app:editingHint|label}** gale bakstelėkite **kameros** piktogramą.
3. Pasirinkite **{app:newSceneCamera}**, jei norite nufotografuoti dabar, arba **{app:newSceneGallery}**, jei norite naudoti jau turimą nuotrauką.
4. **{app:sceneCropTitle}**: patempkite kampus taip, kad tai, apie ką kalbėsite, užpildytų paveikslėlį, tada bakstelėkite **{app:sceneCropDone}**. Arba bakstelėkite **{app:sceneCropWhole}**. Vaiko ekrane vaizdas nepadidinamas, todėl kuo glaudžiau apkarpysite, tuo didesnės bus sritys.
5. Lauke **{app:sceneName}** įrašykite pavadinimą, pavyzdžiui, „Žaidimų aikštelė“.
6. Pasirinkite, **kur bus scenos mygtukas** (žr. toliau).

Tada scena atsidaro, ir galite brėžti jos sritis. Visą šį laiką suaugusiųjų nustatymai lieka atidaryti.

## Kur dedamas mygtukas

Amalino niekada pati nededa naujo mygtuko bet kur. Lange **{app:pickCellTitle}** parodoma lenta:

- Laisvi langeliai paryškinti, o pirmasis iš jų jau pasirinktas. Bakstelėkite **{app:pickCellPutHere}** arba prieš tai bakstelėkite kitą laisvą langelį.
- Langelyje, kuriame yra paslėptas žodis, tai parašyta, ir jo pasirinkti negalima: tas žodis vėliau atsiras ten. Pavyzdžiui, aplanke gali būti parašyta: {app:pickCellHiddenWord|word=šokinėti|level=3}.
- Vienas langelis pažymėtas užrašu **{app:pickCellFavouritesNote}**.
- Mygtukas **{app:pickCellFavouritesInstead}** įdeda mygtuką į aplanką „{app:favourites}“.
- Jei lenta pilna, Amalino parašo **{app:pickCellBoardFull}** Pasirinkite **{app:pickCellFavouritesInstead}** arba **{app:pickCellChooseAnother}**.

Mygtukas **{app:back}** grąžina prie pavadinimo. Jei išeinate nepadėję mygtuko, Amalino paklausia: **{app:discardSceneQuestion}** Nuotrauka ištrinama tik jums patvirtinus.

## Kalbančių vietų brėžimas

**Kalbanti vieta** – tai nuotraukos sritis, kuri prabyla, kai vaikas ją bakstelėja. Kai scenoje kalbančių vietų dar nėra, ant nuotraukos esanti kortelė paaiškina, ką daryti.

- **Stačiakampis**: vienu pirštu nubrėžkite stačiakampį ant daikto. Įveskite žodį (arba įrašykite jį balsu), tada bakstelėkite **{app:save}**.
- **Bet kokia kita forma**: bakstelėkite **{app:scenePolygon}**, vieną po kito bakstelėkite kampus aplink daiktą, tada bakstelėkite **{app:done}**. Formai reikia bent trijų kampų.
- **Srities keitimas**: palaikykite sritį nuspaudę, kol atsidarys jos redagavimo langas. Galite pakeisti žodį, įrašyti savo balsą arba ją ištrinti (**{app:delete}**).
- **Didinimas**: kai brėžiate mažas sritis, nuotrauką padidinkite suglausdami arba išskėsdami du pirštus. Vienu pirštu visada brėžiama.

Scenos redagavimo lango viršuje esantys mygtukai:

- **{app:sceneOutlines}**: vaikui parodomas kiekvienos srities kraštas – tamsi ir šviesi linija, kad būtų matyti bet kokioje nuotraukoje.
- **{app:sceneTouchAreas}**: jums parodoma, kokio dydžio kiekviena sritis yra liečiant, pritaikius lietimo nustatymus.
- **{app:sceneWordOnTap}**: kol žodis ištariamas, jis rodomas šalia srities (pagal numatytuosius nustatymus įjungta).
- **{app:sceneWordsAlways}**: kiekvienos srities žodis rodomas visą laiką (pagal numatytuosius nustatymus išjungta).
- **{app:sceneChangeCrop}**: nuotrauka apkarpoma iš naujo. Amalino parodo, kiek kalbančių vietų atsidurs už naujojo apkarpymo ribų. Jos neištrinamos ir sugrįžta, jei apkarpymą vėl padidinsite.

Mažuose ekranuose šie mygtukai išsidėsto dviem ar trimis eilėmis.

Kai scena atidaryta, kameros meniu yra ir punktas **{app:suggestHotspots}**: Amalino įrenginyje išanalizuoja nuotrauką ir pasiūlo sritis. Nuimkite žymes nuo nereikalingų ir bakstelėkite **{app:addSelected}**. Android įrenginiuose tam naudojama Google ML Kit, o iPhone ir iPad – Apple Vision, abu veikia pačiame įrenginyje: nuotrauka jo niekada nepalieka. Žr. [Privatumas](privacy.md).

Baigę viršutinėje juostoje bakstelėkite **{app:done}**.

## Ką mato vaikas

Scena atsidaro iš savo mygtuko lentoje, kaip aplankas. Kai vaikas bakstelėja sritį:

- ištariamas jos žodis,
- kai įjungta **{app:sceneWordOnTap}**, žodis dideliomis raidėmis pasirodo virš pat srities (jei ten nėra vietos – po ja) ir netrukus po garso išblunka,
- kai įjungta **{app:reduceMotion}**, žodis pasirodo ir išnyksta be išblukimo.

Žodžiai niekada netrukdo: bakstelėjimas ant žodžio pasiekia po juo esančią sritį.

## Kaip vėliau perkelti scenos mygtuką

Lentoje atidarykite scenos mygtuko redagavimo langą ir pasirinkite **{app:sceneMove}** Galite pasirinkti kitą langelį toje pačioje lentoje, pasirinkti kitą lentą arba įdėti mygtuką į aplanką „{app:favourites}“. Žr. [Redagavimas ir mygtukų perkėlimas](editing.md).

Toliau: [Redagavimas ir mygtukų perkėlimas](editing.md).
