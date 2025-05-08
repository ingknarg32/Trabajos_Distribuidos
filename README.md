# Web Crawler y Generador de Nube de Palabras

Este proyecto consiste en un web crawler que extrae citas de [quotes.toscrape.com](https://quotes.toscrape.com/) y genera una nube de palabras a partir de ellas

## Características

- Web scraping de citas usando BeautifulSoup4
- Generación de nubes de palabras personalizadas
- API FastAPI para funcionalidades web (opcional)

## Requisitos

```bash
pip install -r requirements.txt
```

## Uso

Para generar una nube de palabras:

```bash
python cloudword.py
```

Esto generará:
1. Un archivo `TITULOS.txt` con las citas extraídas
2. Una imagen `mi_nube.png` con la nube de palabras

## Estructura del Proyecto

- `webscraper.py`: Módulo para extraer citas de la web
- `cloudword.py`: Generador de nubes de palabras
- `main.py`: API FastAPI (si se desea usar)
- `requirements.txt`: Dependencias del proyecto