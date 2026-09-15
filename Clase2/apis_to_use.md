# APIs a probar

## 1. Tiempo metereológico - Open-Meteo API

Información sobre tiempo meteorológico, con opciones a diferentes filtros.

🔗 URL: [https://open-meteo.com/en/docs](https://open-meteo.com/en/docs)

---

## 2. Perros - Dog CEO API

Imágenes de perros, con opciones de distinguir por razas.

🔗 URL: [https://dog.ceo/dog-api/](https://dog.ceo/dog-api/)

---

## 3. Gatos - Cat Fact API

Datos curiosos sobre gatos.

🔗 URL: [https://catfact.ninja/](https://catfact.ninja/)

---

## 4. Trivial - Open Trivia Database

Preguntas del Trivial.

🔗 URL: [https://opentdb.com/](https://opentdb.com/)

---

## 5. Libros - Open Library Books API

Datos sobre libros: búsqueda por ISBN (Books API) y búsqueda por tema (Search API).

> ⚠️ El endpoint `/api/books` está marcado como *legacy* en la documentación oficial y podría retirarse en el futuro. Las alternativas recomendadas son la Search API o `/isbn/{isbn}.json`.
>
> Límite de uso: 1 petición/segundo sin identificarse, o 3 peticiones/segundo enviando una cabecera `User-Agent` con el nombre de la aplicación y un email de contacto.

🔗 URL: [https://openlibrary.org/dev/docs/api/books](https://openlibrary.org/dev/docs/api/books)

🔗 Search API: [https://openlibrary.org/dev/docs/api/search](https://openlibrary.org/dev/docs/api/search)