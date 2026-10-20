<!-- description: Lav en scene i Amalino: Tag et foto, beskær det, vælg, hvor knappen skal stå, og tegn områder, der taler – med ordet vist ved tryk. -->
# Scener

En **scene** er et foto med områder, der taler, når barnet trykker på dem: legepladsen med gyngen og rutsjebanen, køkkenbordet, mormors have. Barnet trykker på gyngen og hører »gynge«. Scener er gode til små børn og til at tale om rigtige steder og oplevelser.

## Lav en ny scene

1. Åbn voksenindstillingerne, og vælg **{app:editBoard}**.
2. Tryk på **kameraikonet** for enden af linjen **{app:editingHint|label}** under den øverste bjælke.
3. Vælg **{app:newSceneCamera}** for at tage et foto nu eller **{app:newSceneGallery}** for at bruge et, du allerede har.
4. **{app:sceneCropTitle}**: Træk i hjørnerne, så de ting, I skal tale om, fylder billedet, og tryk på **{app:sceneCropDone}**. Du kan også trykke på **{app:sceneCropWhole}**. Barnets visning zoomer ikke, så jo tættere du beskærer, desto større bliver områderne.
5. Skriv et navn under **{app:sceneName}**, for eksempel »Legepladsen«.
6. Vælg, **hvor scenens knap skal stå** (se nedenfor).

Derefter åbner scenen, og du kan tegne dens områder. Voksenindstillingerne er åbne hele vejen igennem.

## Hvor knappen skal stå

Amalino placerer aldrig selv en ny knap. **{app:pickCellTitle}** viser tavlen:

- De ledige felter er fremhævet, og det første er allerede valgt. Tryk på **{app:pickCellPutHere}**, eller tryk først på et andet ledigt felt.
- Et felt, der rummer et skjult ord, viser det og kan ikke vælges: Ordet dukker op dér senere. I en mappe kan der for eksempel stå: *{app:pickCellHiddenWord|word=hoppe|level=3}*.
- Ét felt er mærket **{app:pickCellFavouritesNote}**.
- **{app:pickCellFavouritesInstead}** lægger knappen i mappen {app:favourites}.
- Er tavlen fuld, skriver Amalino **{app:pickCellBoardFull}** Vælg **{app:pickCellFavouritesInstead}** eller **{app:pickCellChooseAnother}**.

**{app:back}** fører dig tilbage til navnet. Går du ud uden at placere knappen, spørger Amalino »{app:discardSceneQuestion}« og sletter kun billedet, hvis du bekræfter.

## Tegn områder, der taler

Et **område, der taler**, er en del af fotoet, som siger noget, når barnet trykker på det. Har en scene endnu ingen områder, står der på et kort på fotoet, hvad du skal gøre.

- **En ramme**: Træk en ramme hen over tingen med én finger. Skriv ordet (eller indtal det), og tryk på **{app:save}**.
- **Alle andre former**: Tryk på **{app:scenePolygon}**, tryk på hjørnerne rundt om tingen ét ad gangen, og tryk på **{app:done}**. En form skal have mindst tre hjørner.
- **Ret et område**: Hold fingeren på det, indtil redigeringen åbner. Du kan ændre ordet, indtale det med din stemme eller vælge **{app:delete}**.
- **Zoom**: Knib med to fingre for at zoome ind på fotoet, når du tegner små områder. Med én finger tegner du altid.

Knapperne øverst i redigeringen af scenen:

- **{app:sceneOutlines}**: viser barnet kanten af hvert område som en mørk og en lys streg, så den kan ses på ethvert foto.
- **{app:sceneTouchAreas}**: viser dig, hvor stort hvert område er at trykke på, når berøringsindstillingerne er regnet med.
- **{app:sceneWordOnTap}**: viser ordet ved området, mens det bliver sagt (slået til som standard).
- **{app:sceneWordsAlways}**: viser hele tiden ordet for hvert område (slået fra som standard).
- **{app:sceneChangeCrop}**: beskærer fotoet igen. Amalino fortæller dig, hvor mange områder der falder uden for den nye beskæring. De bliver ikke slettet og kommer tilbage, hvis du gør beskæringen større igen.

På små skærme fordeler knapperne sig på to eller tre rækker.

Mens en scene er åben, tilbyder kameramenuen også **{app:suggestHotspots}**: Amalino ser på fotoet på enheden og foreslår områder. Fjern fluebenet ved dem, du ikke vil have, og tryk på **{app:addSelected}**. På Android bruges Google ML Kit og på iPhone og iPad Apple Vision – begge på enheden, så fotoet forlader den aldrig. Læs mere under [Privatliv](privacy.md).

Tryk på **{app:done}** i den øverste bjælke, når du er klar.

## Det ser barnet

Scenen åbner fra sin knap på tavlen, ligesom en mappe. Når barnet trykker på et område:

- bliver ordet sagt,
- med **{app:sceneWordOnTap}** slået til vises ordet med store bogstaver lige over området (eller under det, hvis der ikke er plads) og toner ud kort efter, at lyden er slut,
- med **{app:reduceMotion}** slået til dukker ordet op og forsvinder igen uden at tone ud.

Ordene er aldrig i vejen: Et tryk på et ord når igennem til området nedenunder.

## Flyt en scenes knap senere

Redigér scenens knap på tavlen, og vælg **{app:sceneMove}**. Du kan vælge et andet felt på samme tavle, vælge en anden tavle eller lægge knappen i {app:favourites}. Læs mere under [Redigér og flyt knapper](editing.md).

Næste side: [Redigér og flyt knapper](editing.md).
