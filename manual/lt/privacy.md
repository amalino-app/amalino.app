<!-- description: Ką Amalino laiko įrenginyje, ką ir kada atsisiunčia ir kas (jei apskritai kas) palieka įrenginį. Be reklamos, be sekimo, be paskyros. -->
# Privatumas

Amalino sukurta taip, kad vaiko žodžiai liktų su vaiku. Nėra jokios reklamos, jokio sekimo ir jokios paskyros.

## Kas lieka įrenginyje

- Vaiko lentos, žodžiai, nuotraukos ir įrašai.
- Tai, ką vaikas sako, ir naudojimo žurnalai, kuriais remiasi skiltis **{app:progress}** ir jos santrauka **{app:thisWeek}**.
- Vaiko vardas.

Visa tai saugoma tik įrenginyje, užšifruota. Man tai niekada nesiunčiama.

## Atsarginės kopijos

- **Automatinė kasdienė atsarginė kopija** lieka įrenginyje ir atsidaro tik jame.
- Funkcija **{app:exportBackup}** sukuria jūsų slaptažodžiu apsaugotą failą, kurį galėsite perkelti į naują įrenginį. Kur jį laikyti, sprendžiate patys.
- **iPhone ir iPad**: jei darote įrenginio atsarginę kopiją iCloud saugykloje ar kompiuteryje, į ją patenka ir Amalino duomenys.
- **Android**: Amalino duomenys nekopijuojami nei į jūsų Google atsarginę kopiją, nei į naują telefoną.

Žr. [Dalijimasis ir spausdinimas](sharing-and-printing.md).

## Ką Amalino atsisiunčia

Kai kas atsisiunčiama vieną kartą, kai to paprašote, o paskui veikia be interneto. Jokia informacija apie vaiką nesiunčiama.

- **Balsai**: natūralūs balsai, vienas atsisiuntimas visoms kalboms, iš GitHub platformos (github.com/amalino-app/voices arba, jei ten nepasiekiama, iš pirminio sherpa-onnx leidimo). Amalino pirmiausia nurodo dydį ir paklausia prieš naudodama mobilųjį internetą.
- **Kalbos atpažinimas** funkcijai **{app:aiListen}** – iš GitHub platformos (k2-fsa/sherpa-onnx).
- **Paveikslėliai**: jei ieškote visoje ARASAAC kolekcijoje ar kituose simbolių rinkiniuose internete (Global Symbols), siunčiami tik jūsų paieškos žodžiai. Pasirinkti paveikslėliai išsaugomi įrenginyje.
- **Vertimas be interneto**: Android įrenginyje – Google ML Kit vertimo modelis, vieną kartą kiekvienai kalbai. iPhone ir iPad įrenginiuose kalbos gaunamos iš pačios Apple programėlės Translate nustatymų. Jokie programėlės žodžiai nesiunčiami.

## Funkcijos, veikiančios įrenginyje

- Funkcija **{app:aiListen}** kalbą atpažįsta įrenginyje. Garsas niekada neįrašomas ir niekur nesiunčiamas.
- Funkcija **{app:contextBoards}** remiasi tik paros laiku. Amalino nenaudoja nei jūsų buvimo vietos, nei kalendoriaus.
- Funkcija **{app:suggestHotspots}** scenos nuotrauką analizuoja įrenginyje. Android įrenginiuose ji naudoja Google ML Kit: nuotraukos niekada nepalieka įrenginio, tačiau ML Kit siunčia bendrovei Google anoniminę informaciją apie tai, kaip funkcija veikia ir kaip ja naudojamasi. Tas pats galioja ir vertimui be interneto Android įrenginiuose. iPhone ir iPad naudoja Apple Vision, irgi pačiame įrenginyje.

## Kas gali palikti įrenginį

Be minėtos anoniminės ML Kit informacijos ir jūsų interneto (IP) adreso, kai Amalino ką nors atsisiunčia, įrenginį palieka tik tai, ką nusprendžiate išsiųsti patys:

- atsarginės kopijos failas, kurį eksportuojate ir kuriuo pasidalijate,
- lentos, kurias eksportuojate į kitą programėlę,
- atspausdintas arba išsaugotas PDF failas.

Funkcijų, kurioms reikėtų internetinės paslaugos (**{app:syncTitle}**, **{app:library}** ir debesijos pagalbininkai suaugusiesiems), šioje programėlės versijoje nėra.

## Kaip viską ištrinti

Pašalinus programėlę, ištrinama viskas, ką ji laikė įrenginyje. Jei vėliau norėsite duomenis atkurti, pasilikite eksportuotą atsarginę kopiją.

Visa privatumo politika pateikta svetainės [privatumo puslapyje](site:privacy); joje aprašyta ir pati svetainė. Programėlėje nuoroda į ją yra skiltyje **{app:about}** ir sąrankos pabaigoje.
