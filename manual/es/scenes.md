<!-- description: Crea una escena en Amalino: haz una foto, recórtala, elige dónde va su botón y dibuja zonas que hablan, con la palabra a la vista al tocarlas. -->
# Escenas

Una **escena** es una foto con zonas que hablan, es decir, partes de la foto que dicen algo cuando el niño las toca: el parque con el columpio y el tobogán, la mesa de la cocina, el jardín de la abuela. El niño toca el columpio y oye «columpio». Las escenas funcionan muy bien con niños pequeños y para hablar de lugares y momentos reales.

## Crear una escena nueva

1. Abre los controles para adultos y elige **{app:editBoard}**.
2. En la línea **{app:editingHint|label}**, debajo de la barra superior, toca el icono de la **cámara** que hay al final.
3. Elige **{app:newSceneCamera}** para hacer una foto en ese momento, o **{app:newSceneGallery}** para usar una que ya tengas.
4. **{app:sceneCropTitle}**: arrastra las esquinas para que lo que vas a nombrar llene la imagen y toca **{app:sceneCropDone}**. O toca **{app:sceneCropWhole}**. La vista del niño no hace zoom, así que un recorte ajustado hace que las zonas sean más grandes.
5. Escribe un nombre en **{app:sceneName}**, por ejemplo «Parque».
6. Elige **dónde va el botón de la escena** (lo explico más abajo).

Después se abre la escena, lista para que dibujes sus zonas. Los controles para adultos siguen abiertos durante todo el proceso.

## Dónde va el botón

Amalino nunca coloca un botón nuevo por su cuenta. **{app:pickCellTitle}** muestra el tablero:

- Las casillas libres aparecen resaltadas, y la primera ya está elegida. Toca **{app:pickCellPutHere}**, o toca antes otra casilla libre.
- Una casilla que guarda una palabra oculta lo indica y no se puede elegir: esa palabra aparecerá ahí más adelante. En una carpeta, por ejemplo, puede decir *{app:pickCellHiddenWord|word=saltar|level=3}*.
- Una casilla aparece marcada con **{app:pickCellFavouritesNote}**.
- **{app:pickCellFavouritesInstead}** pone el botón en la carpeta {app:favourites}.
- Si el tablero está lleno, Amalino dice **{app:pickCellBoardFull}** Elige **{app:pickCellFavouritesInstead}** o **{app:pickCellChooseAnother}**.

**{app:back}** vuelve al nombre. Si sales sin colocar el botón, Amalino pregunta: *{app:discardSceneQuestion}* La foto solo se borra si lo confirmas.

## Dibujar zonas que hablan

Una **zona que habla** es una parte de la foto que dice algo cuando el niño la toca. Mientras una escena no tiene ninguna, una tarjeta sobre la foto explica qué hacer.

- **Un recuadro**: con un dedo, arrastra un recuadro sobre la cosa. Escribe la palabra (o grábala) y toca **{app:save}**.
- **Cualquier otra forma**: toca **{app:scenePolygon}**, ve tocando una a una las esquinas alrededor de la cosa y toca **{app:done}**. Una forma necesita al menos tres esquinas.
- **Cambiar una zona**: mantenla pulsada hasta que se abra su editor. Puedes cambiar la palabra, grabar tu voz o **{app:delete}** la zona.
- **Zoom**: pellizca con dos dedos para ampliar la foto mientras dibujas zonas pequeñas. Con un dedo, siempre se dibuja.

Los botones de la parte superior del editor de escenas:

- **{app:sceneOutlines}**: muestra al niño el borde de cada zona, con una línea oscura y otra clara, para que se distinga sobre cualquier foto.
- **{app:sceneTouchAreas}**: te muestra cómo de grande es cada zona al tocarla, con los ajustes táctiles aplicados.
- **{app:sceneWordOnTap}**: muestra la palabra cerca de la zona mientras se dice (activado de forma predeterminada).
- **{app:sceneWordsAlways}**: muestra todo el tiempo la palabra de cada zona (desactivado de forma predeterminada).
- **{app:sceneChangeCrop}**: vuelve a recortar la foto. Amalino te dice cuántas zonas quedan fuera del nuevo recorte. No se borran, y vuelven si haces el recorte más grande.

En las pantallas pequeñas, estos botones ocupan dos o tres filas.

Con una escena abierta, el menú de la cámara también ofrece **{app:suggestHotspots}**: Amalino analiza la foto en el dispositivo y propone zonas. Desmarca las que no quieras y toca **{app:addSelected}**. En Android se usa Google ML Kit, y en iPhone y iPad, Vision de Apple, ambos en el propio dispositivo: la foto nunca sale de él. Lo explico en [Privacidad](privacy.md).

Cuando termines, toca **{app:done}** en la barra superior.

## Lo que ve el niño

La escena se abre desde su botón en el tablero, como una carpeta. Cuando el niño toca una zona:

- se dice su palabra;
- con **{app:sceneWordOnTap}**, la palabra aparece en letras grandes justo encima de la zona (debajo, si no hay sitio) y se desvanece poco después de que termine el sonido;
- con **{app:reduceMotion}** activado, la palabra aparece y desaparece sin desvanecerse.

Las palabras nunca estorban: si se toca una palabra, el toque llega a la zona que hay debajo.

## Mover más tarde el botón de una escena

Edita el botón de la escena en el tablero y elige **{app:sceneMove}** en su editor. Puedes elegir otra casilla del mismo tablero, elegir otro tablero o ponerlo en {app:favourites}. Lo explico en [Editar y mover botones](editing.md).

Siguiente: [Editar y mover botones](editing.md).
