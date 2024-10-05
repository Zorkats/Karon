import os

# Función para búsqueda avanzada de PDF con selectores
async def search_with_advanced_selectors(page, doi):
    try:
        selector = ('a.xpl-btn-pdf, a.coolBar__ctrl.pdf-download, '
                    'a.a-link.pdf.article-pdfLink, a.link-button, '
                    'a[href$=".pdf"], a:has-text("PDF"), '
                    'a.obj_galley_link.pdf, a.pdfLink, '
                    'button#download, a.xpl-btn-pdf, '
                    'a.al-link.pdf.openInAnotherWindow, '
                    'a.btn-primary.js-download-btn, div#download-modal-trigger')
        pdf_button = await page.query_selector(selector)

        if pdf_button:
            pdf_url = await pdf_button.get_attribute('href')
            if pdf_url and not pdf_url.startswith('http'):
                pdf_url = page.url + pdf_url
            return pdf_url
        return None

    except Exception as e:
        print(f"Error en la búsqueda avanzada para DOI {doi}: {e}")
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

        if pdf_url and not pdf_url.startswith('http'):
            pdf_url = page.url + pdf_url
        return pdf_url

    except Exception as e:
        print(f"Error en la búsqueda general para DOI {doi}: {e}")
        return None

