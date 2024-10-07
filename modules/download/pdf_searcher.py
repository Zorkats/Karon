import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')
from modules.download.pdf_downloader import download_and_save_pdf_stream
from utils import get_download_path

download_folder = get_download_path()

# Función para búsqueda avanzada de PDF con selectores
async def search_with_advanced_selectors(page, doi):

    try:
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

            # Si la URL no empieza con http, verificar si es relativa o ya está completa
            if pdf_url and not pdf_url.startswith('http'):
                # Revisar si es relativa o si ya incluye parte del dominio
                if not pdf_url.startswith('/'):
                    pdf_url = '/' + pdf_url  # Asegurarse de que la URL es correcta si falta la barra inicial.
                pdf_url = page.url.split('/')[0] + "//" + page.url.split('/')[2] + pdf_url
            
            return pdf_url  # Devolver la URL del PDF si se encuentra
        else:
            return None  # Devolver None si no se encuentra el PDF
    except Exception as e:
        print(f"Error al buscar el PDF con selectores avanzados: {e}")
        return None


async def search_with_general_method(page, doi):
    try:
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

        # Verificar si la URL no empieza con http y construirla correctamente si es relativa
        if pdf_url and not pdf_url.startswith('http'):
            if not pdf_url.startswith('/'):
                pdf_url = '/' + pdf_url
            pdf_url = page.url.split('/')[0] + "//" + page.url.split('/')[2] + pdf_url

        return pdf_url if pdf_url else None
    except Exception as e:
        print(f"Error en el método general de búsqueda de PDF: {e}")
        return None


