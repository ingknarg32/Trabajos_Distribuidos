import pandas as pd
import numpy as np 
from PIL import Image 
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS

def cloudwords_news_uno(txt_file, output_image='nube_palabras.png'):
    with open(txt_file, 'r', encoding='utf-8') as file:
        texto = file.read()
        
    stopwords = set(STOPWORDS)

    txt_wc = WordCloud(
        background_color='white',
        max_words=100,
        width=800,
        height=400,
        stopwords=stopwords,
        prefer_horizontal=0.7,
        collocations=False,
        min_font_size=10,
        max_font_size=100
    )
    txt_wc.generate(texto)
    
    plt.figure(figsize=(10, 8))
    plt.imshow(txt_wc, interpolation='bilinear')
    plt.axis('off')
    plt.show()
    
    txt_wc.to_file(output_image)
    print(f"Nube de palabras guardada como: {output_image}")

if __name__ == "__main__":
    # First run the webscraper to generate the TITULOS.txt file
    import webscraper
    df = webscraper.scrape_quotes()
    webscraper.save_to_txt_file(df, 'TITULOS.txt')
    
    # Then generate the word cloud
    cloudwords_news_uno("TITULOS.txt", "mi_nube.png")
