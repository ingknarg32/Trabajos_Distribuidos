# main.py
from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
import nltk
import re

# Descargar recursos necesarios de NLTK
try:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
except:
    print("Error downloading NLTK resources")

# --- Metadata de la API (Opcional pero bueno para la documentación) ---
description = """
API para extraer información de libros (títulos y precios) desde books.toscrape.com. 🚀

## Funcionalidad

* **GET /crawl**: Inicia el proceso de scraping y devuelve los datos encontrados.
"""

tags_metadata = [
    {
        "name": "Crawler",
        "description": "Operaciones relacionadas con el web scraping.",
    }
]

# --- Inicialización de FastAPI ---
app = FastAPI(
    title="Web Crawler API - BooksToScrape",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    # Puedes añadir más metadata como contact, license_info, etc.
)

# --- Lógica del Crawler ---
def lemmatize_text(text: str) -> str:
    """Procesa el texto para crear lemmatización."""
    # Tokenización y limpieza
    text = re.sub(r'[^\w\s]', '', text.lower())
    tokens = word_tokenize(text)
    
    # Eliminar stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Lematización
    lemmatizer = WordNetLemmatizer()
    lemmas = [lemmatizer.lemmatize(token) for token in tokens]
    
    return ' '.join(lemmas)

def generate_wordcloud(text: str) -> str:
    """Genera una nube de palabras a partir de un texto."""
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    # Guardar la imagen en memoria
    img_buffer = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(img_buffer, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    img_buffer.seek(0)
    
    # Convertir la imagen a base64
    return base64.b64encode(img_buffer.getvalue()).decode()

def scrape_books() -> List[Dict[str, Any]]:
    """
    Realiza el web scraping en books.toscrape.com y extrae títulos y precios.
    Devuelve una lista de diccionarios, cada uno representando un libro.
    Maneja errores básicos de conexión y parsing.
    """
    URL = "http://books.toscrape.com/"
    books_data = []

    try:
        # Realizar la petición GET con timeout
        response = requests.get(URL, timeout=10)
        # Verificar si la petición fue exitosa (código 2xx)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        # Manejar errores de red (timeout, DNS error, etc.)
        print(f"Error de red al acceder a {URL}: {e}")
        # Podrías devolver el error o lanzar una excepción específica de la app
        # Devolver una lista vacía o un mensaje de error podría ser una opción:
        # return [{"error": "No se pudo conectar al sitio web."}]
        # Por simplicidad, lanzaremos una excepción que FastAPI manejará como error 500
        raise HTTPException(status_code=503, detail=f"No se pudo conectar a {URL}: {e}")

    # Parsear el contenido HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontrar todos los contenedores de libros (etiqueta <article class="product_pod">)
    book_articles = soup.find_all('article', class_='product_pod')

    if not book_articles:
        print("No se encontraron artículos de libros en la página.")
        return [] # Devolver lista vacía si no se encuentran libros

    # Iterar sobre cada libro encontrado
    for book in book_articles:
        try:
            # Extraer el título (está en el atributo 'title' de la etiqueta <a> dentro de <h3>)
            # Se añade manejo de errores por si la estructura cambia
            title_tag = book.h3.a
            title = title_tag['title'] if title_tag and 'title' in title_tag.attrs else "Título no encontrado"

            # Extraer el precio (está en la etiqueta <p class="price_color">)
            price_tag = book.find('p', class_='price_color')
            price = price_tag.text if price_tag else "Precio no encontrado"

            # Procesar el título para lemmatización
            lemmatized_text = lemmatize_text(title)
            
            books_data.append({
                "title": title,
                "price": price,
                "lemmatized_title": lemmatized_text
            })
        except AttributeError as e:
            # Manejar el caso donde un libro específico no tenga la estructura esperada
            print(f"Error al parsear un libro: {e}. Libro omitido.")
            # O podrías añadir un registro con error:
            # books_data.append({"error": "Error de parseo", "details": str(e)})
            continue # Saltar al siguiente libro

    return books_data

# --- Endpoints de la API ---
@app.get("/crawl",
         response_model=List[Dict[str, Any]], # Define la estructura esperada de la respuesta
         tags=["Crawler"], # Agrupa el endpoint en la documentación
         summary="Extraer datos de libros",
         description="Realiza scraping en books.toscrape.com y devuelve una lista de libros con título y precio."
         )
async def crawl_website():
    """Endpoint que activa el crawler y devuelve los datos extraídos."""
    print("Iniciando proceso de crawling...")
    scraped_data = scrape_books()
    if not scraped_data:
        print("No se extrajeron datos.") # Log para el servidor
    else:
        print(f"Se extrajeron {len(scraped_data)} libros.")
    return scraped_data

@app.get("/wordcloud/{book_index}",
         tags=["WordCloud"],
         summary="Generar nube de palabras",
         description="Genera una nube de palabras para un libro específico basado en su índice."
         )
async def get_wordcloud(book_index: int):
    """Endpoint para generar la nube de palabras de un libro específico."""
    scraped_data = scrape_books()
    
    if not scraped_data:
        raise HTTPException(status_code=404, detail="No hay libros disponibles")
    
    if book_index < 0 or book_index >= len(scraped_data):
        raise HTTPException(status_code=404, detail="Índice de libro no válido")
    
    book = scraped_data[book_index]
    wordcloud_image = generate_wordcloud(book['lemmatized_title'])
    
    return {
        "title": book['title'],
        "wordcloud": wordcloud_image
    }

@app.get("/wordcloud/all",
         tags=["WordCloud"],
         summary="Generar nubes de palabras para todos los libros",
         description="Genera nubes de palabras para todos los libros disponibles."
         )
async def get_all_wordclouds():
    """Endpoint para generar nubes de palabras de todos los libros."""
    scraped_data = scrape_books()
    
    if not scraped_data:
        raise HTTPException(status_code=404, detail="No hay libros disponibles")
    
    result = []
    for i, book in enumerate(scraped_data):
        wordcloud_image = generate_wordcloud(book['lemmatized_title'])
        result.append({
            "index": i,
            "title": book['title'],
            "wordcloud": wordcloud_image
        })
    
    return result

# --- (Opcional) Ejecutar con Uvicorn para pruebas locales ---
# Esto permite ejecutar el script directamente con `python main.py`
if __name__ == "__main__":
    import uvicorn
    print("Iniciando servidor Uvicorn en http://127.0.0.1:8080")
    # host="0.0.0.0" para que sea accesible desde fuera de localhost si es necesario
    uvicorn.run(app, host="127.0.0.1", port=8080)