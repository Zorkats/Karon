import os
import pandas as pd

# Función para obtener los DOIs de los archivos ya descargados
def get_downloaded_papers(download_folder):
    downloaded_papers = set()
    for file_name in os.listdir(download_folder):
        if file_name.endswith('.pdf'):
            # Convertir el nombre del archivo de nuevo a un DOI (eliminar ".pdf" y reemplazar "_" por "/")
            doi = file_name.replace('.pdf', '').replace('_', '/')
            downloaded_papers.add(doi)
    return downloaded_papers

# Función para comparar los DOIs en el CSV con los ya descargados
def filter_papers_to_download(csv_path, download_folder):
    # Obtener los DOIs del CSV
    df = pd.read_csv(csv_path)
    dois_in_csv = set(df['DOI'].tolist())

    # Obtener los DOIs de los archivos ya descargados
    downloaded_dois = get_downloaded_papers(download_folder)

    # Imprimir los DOIs descargados y los que faltan (debug)
    print("DOIs en la carpeta de descargas:", downloaded_dois)
    print("DOIs en el CSV:", dois_in_csv)

    # Filtrar los DOIs que aún no se han descargado
    dois_to_download = list(dois_in_csv - downloaded_dois)
    
    # Imprimir los DOIs que faltan por descargar (debug)
    print("DOIs pendientes de descargar:", dois_to_download)
    
    return dois_to_download
