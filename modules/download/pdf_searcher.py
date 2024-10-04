import os
from modules.download.pdf_downloader import download_and_save_pdf_stream

# Función para búsqueda avanzada de PDF con selectores
async def search_with_advanced_selectors(page, doi, download_folder):
    try:
        print(f"Esperando a que la página se cargue para el DOI {doi}...")
        await page.wait_for_load_state('load')  # Asegúrate de que la página esté completamente cargada

        print(f"Buscando PDF con selectores avanzados para DOI {doi}...")
        selector = ('a.xpl-btn-pdf, a.coolBar__ctrl.pdf-download, '
                    'a.a-link.pdf.article-pdfLink, a.link-button, '
                    'a[href$=".pdf"], a:has-text("PDF"), '
                    'a.obj_galley_link.pdf, a.pdfLink, '
                    'button#download, a.xpl-btn-pdf, '
                    'a.al-link.pdf.openInAnotherWindow, '
                    'a.btn-primary.js-download-btn, div#download-modal-trigger, '
                    'a.navbar-download.btn--cta_roundedColored, '
                    'a.article_btn_secondary[data-id="article_header_OpenPDF"], '
                    'a.navbar-download.btn--cta_roundedColored[data-single-download="true"]')

        pdf_button = await page.query_selector(selector)

        if pdf_button:
            pdf_url = await pdf_button.get_attribute('href')
            print(f"PDF URL encontrado con selectores avanzados: {pdf_url}")
            if pdf_url and not pdf_url.startswith('http'):
                pdf_url = page.url + pdf_url

            # Descargar y guardar el PDF usando download_and_save_pdf_stream
            if pdf_url:
                download_folder = os.path.join(os.path.abspath(os.getcwd()), 'downloads')
                download_complete = await download_and_save_pdf_stream(pdf_url, doi, download_folder)
                if download_complete:
                    print(f"Descarga completa con selectores avanzados para {doi}")
                    return True
        else:
            print(f"No se encontró PDF con selectores avanzados para {doi}")
        return False

    except Exception as e:
        print(f"Error en la búsqueda avanzada para DOI {doi}: {e}")
        return False


# Función para búsqueda general de PDF en la página
async def search_with_general_method(page, doi, download_folder):
    try:
        print(f"Esperando a que la página se cargue para el DOI {doi}...")
        await page.wait_for_load_state('load')  # Asegúrate de que la página esté completamente cargada

        print(f"Buscando PDF con el método general para DOI {doi}...")
        pdf_url = await page.evaluate('''() => {
            let anchors = [...document.querySelectorAll('a')];
            for (let anchor of anchors) {
                let text = anchor.textContent || '';
                if (text.includes('Download PDF') || text.includes('PDF')) {
                    return anchor.href;
                }
            }
            return null;
        }''')

        if pdf_url:
            print(f"PDF URL encontrado con el método general: {pdf_url}")
            if not pdf_url.startswith('http'):
                pdf_url = page.url + pdf_url

            # Descargar y guardar el PDF usando download_and_save_pdf_stream
            download_folder = os.path.join(os.path.abspath(os.getcwd()), 'downloads')
            download_complete = await download_and_save_pdf_stream(pdf_url, doi, download_folder)
            if download_complete:
                print(f"Descarga completa con el método general para {doi}")
                return True
        else:
            print(f"No se encontró PDF con el método general para {doi}")

        return False

    except Exception as e:
        print(f"Error en la búsqueda general para DOI {doi}: {e}")
        return False
