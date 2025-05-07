import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_quotes():
    url = 'https://quotes.toscrape.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    quotes = []
    authors = []

    for quote_block in soup.find_all("div", class_="quote"):
        text = quote_block.find("span", class_="text").text
        author = quote_block.find("small", class_="author").text
        quotes.append(text)
        authors.append(author)  

    df = pd.DataFrame({
        'quote': quotes,
        'author': authors
    })

    return df

def save_to_txt_file(df, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        # Concatenar todas las citas con espacios
        text = ' '.join(df['quote'].values)
        file.write(text)
        print('Texto guardado en:', filename)

if __name__ == "__main__":
    df = scrape_quotes()
    save_to_txt_file(df, 'TITULOS.txt')
    print(df)
