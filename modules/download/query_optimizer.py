import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from io import BytesIO

def combine_queries(scopus_path, wos_path=None):
    # Combinar las bases de datos de Scopus y Web of Science
    df_scopus = pd.read_csv(scopus_path)
    
    if wos_path:
        df_wos = pd.read_csv(wos_path)
        df_combined = pd.concat([df_scopus, df_wos], ignore_index=True)
    else:
        df_combined = df_scopus
    return df_combined

def clean_data(df):
    # Limpiar datos: eliminar duplicados y filas sin DOI o Abstract
    # Primero, eliminar duplicados basados en el DOI
    df_cleaned = df.drop_duplicates(subset='DOI')
        
    # Eliminar filas donde la columna 'DOI' es nula
    df_cleaned = df_cleaned.dropna(subset=['DOI'])
        
    # Eliminar filas donde la columna 'Abstract' es nula
    df_cleaned = df_cleaned.dropna(subset=['Abstract'])
        
    return df_cleaned

def filter_by_keyword(df, keyword):
    # Filtrar los resultados según el criterio del usuario
    df_filtered = df[df['Abstract'].str.contains(keyword, case=False, na=False)]
      
    return df_filtered

def plot_publication_year_distribution(df):
    # Asegurarse de que la columna de año exista y sea numérica
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['Year'].dropna().astype(int).value_counts().sort_index().plot(kind='bar')
        plt.xlabel('Year')
        plt.ylabel('Number of Publications')
        plt.title('Publications per Year')
        plt.show()

def plot_wordcloud(df):
    text = ' '.join(df['Abstract'].dropna().values)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Most Common Words in Abstracts')
    
    # Guardar en un objeto BytesIO
    image_data = BytesIO()
    plt.savefig(image_data, format='png')
    plt.close()
    image_data.seek(0)
    return image_data

def generate_report(df, filename='report.html'):
    with open(filename, 'w') as f:
        f.write("<html><head><title>Query Analysis Report</title></head><body>")
        f.write("<h1>Query Analysis Report</h1>")
        f.write(f"<p>Total Articles: {len(df)}</p>")

        # Publicaciones por año
        if 'Year' in df.columns:
            year_count = df['Year'].value_counts().sort_index()
            f.write("<h2>Publications per Year</h2>")
            f.write(year_count.to_frame().to_html())

        # Artículos por autor
        if 'Authors' in df.columns:
            author_count = df['Authors'].value_counts().head(10)
            f.write("<h2>Top 10 Authors</h2>")
            f.write(author_count.to_frame().to_html())

        # Revistas más comunes
        if 'Journal' in df.columns:
            journal_count = df['Journal'].value_counts().head(10)
            f.write("<h2>Top 10 Journals</h2>")
            f.write(journal_count.to_frame().to_html())

        f.write("</body></html>")
    print(f"Report generated and saved as {filename}")

def save_data(df, filename):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")