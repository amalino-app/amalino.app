<!-- description: Qué guarda Amalino en el dispositivo, qué descarga y cuándo, y qué sale del dispositivo, si es que sale algo. Sin anuncios, sin rastreo y sin cuenta. -->
# Privacidad

Amalino está hecho para que las palabras del niño se queden con el niño. No hay anuncios, ni rastreo, ni cuenta.

## Lo que se queda en el dispositivo

- Los tableros, las palabras, las fotos y las grabaciones del niño.
- Lo que dice el niño, y los registros de uso en los que se basan **{app:progress}** y su resumen de **{app:thisWeek}**.
- El nombre del niño.

Todo se guarda únicamente en el dispositivo, cifrado. Nunca me llega a mí.

## Copias de seguridad

- **La copia diaria automática** se queda en el dispositivo y solo se puede abrir en él.
- **{app:exportBackup}** crea un archivo protegido con tu contraseña para pasar los datos a un dispositivo nuevo. Tú decides dónde guardarlo.
- **iPhone y iPad**: si haces una copia de seguridad del dispositivo en iCloud o en un Mac o PC, los datos de Amalino forman parte de esa copia.
- **{app:ga.androidTitle|label}**: los datos de Amalino no se copian en tu copia de seguridad de Google ni se pasan a un teléfono nuevo.

Lo explico en [Compartir e imprimir](sharing-and-printing.md).

## Lo que descarga Amalino

Algunas cosas se descargan una sola vez, cuando tú las pides, y después funcionan sin conexión. No se envía nada sobre el niño.

- **Voces**: las voces naturales, una sola descarga para todos los idiomas, desde GitHub (github.com/amalino-app/voices o, si no está disponible, la publicación original de sherpa-onnx). Amalino te avisa primero de cuánto ocupa y te pregunta antes de usar datos móviles.
- **El reconocimiento de voz** de **{app:aiListen}**, desde GitHub (k2-fsa/sherpa-onnx).
- **Pictogramas**: si buscas en todo ARASAAC o en otros conjuntos de símbolos en línea (Global Symbols), solo se envían las palabras que buscas. Los pictogramas que eliges se guardan en el dispositivo.
- **{app:offlineTranslation|label}**: en Android, el modelo de traducción de ML Kit de Google, una vez para cada idioma. En iPhone y iPad, los idiomas vienen de los ajustes de Traducir de Apple. No se envía ninguna palabra de la app.

## Funciones que trabajan en el dispositivo

- **{app:aiListen}** reconoce el habla en el propio dispositivo. El audio nunca se guarda ni se envía.
- **{app:contextBoards}** solo tiene en cuenta la hora del día. Amalino no usa tu ubicación ni tu calendario.
- **{app:suggestHotspots}** analiza la foto de una escena en el dispositivo. En Android usa Google ML Kit: las fotos nunca salen del dispositivo, pero ML Kit envía a Google información anónima sobre el rendimiento y el uso de la función. Lo mismo ocurre con la traducción sin conexión en Android. El iPhone y el iPad usan Vision de Apple, también en el dispositivo.

## Lo que podría salir del dispositivo

Aparte de la información anónima de ML Kit que acabo de mencionar, y de la dirección de internet (IP) de tu dispositivo cuando Amalino descarga algo, solo sale lo que tú decides enviar:

- un archivo de copia que exportas y compartes,
- los tableros que exportas a otra app,
- un PDF impreso o guardado.

Las funciones que necesitarían un servicio en línea, como **{app:syncTitle}**, la **{app:library}** y las ayudas en la nube, no están en esta versión de la app.

## Borrarlo todo

Al desinstalar la app se borra todo lo que guardaba en el dispositivo. Si quieres restaurar tus datos más adelante, guarda antes una copia exportada.

La política de privacidad completa está en la [página de privacidad](site:privacy) del sitio web, que también trata del propio sitio web. La app enlaza a ella en **{app:about}** y al final de la configuración.
