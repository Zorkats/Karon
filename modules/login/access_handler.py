import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import pandas as pd
import asyncio
from playwright.async_api import async_playwright
from utils import base_dir

# Ruta para guardar el estado de autenticación
auth_state_path = os.path.join(base_dir, 'auth_state.json')
error_log_path = os.path.join(base_dir, 'login_detection_log.txt')

# Función para detectar si el usuario se ha logueado manualmente
async def detect_manual_login(page, doi, error_log):
    try:
        print(f"\nProcesando DOI: {doi}")
        await page.goto(f"https://doi.org/{doi}", wait_until='load', timeout=60000)

        # Esperar a que el usuario inicie sesión manualmente
        input("Inicia sesión manualmente en el sitio y presiona ENTER para continuar...")

        # Guardar el estado del navegador después del login manual
        await page.context.storage_state(path=auth_state_path)
        print(f"Estado de autenticación guardado para {doi}")
        error_log.write(f"{doi} - Estado de autenticación guardado\n")

        return True

    except Exception as e:
        print(f"Error al procesar el DOI {doi}: {e}")
        error_log.write(f"{doi} - Error: {e}\n")
        return False

# Función principal para analizar los DOIs y guardar el estado de login
async def analyze_dois_and_login(papers_path):
    df = pd.read_csv(papers_path)
    dois = df['DOI'].tolist()

    with open(error_log_path, 'w') as error_log:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Para que el usuario pueda interactuar con el navegador
            context = await browser.new_context()

            # Verificar si ya hay un estado de autenticación guardado
            if os.path.exists(auth_state_path):
                await context.add_cookies(await context.storage_state(path=auth_state_path)['cookies'])
                print("Se cargó el estado de autenticación guardado.")

            page = await context.new_page()

            # Iterar sobre los DOIs y permitir el login manual
            for doi in dois:
                await detect_manual_login(page, doi, error_log)

            await browser.close()

# Ejecutar análisis de login manual
if __name__ == '__main__':
    papers_path = os.path.join(base_dir, 'failed_downloads.csv')
    asyncio.run(analyze_dois_and_login(papers_path))
