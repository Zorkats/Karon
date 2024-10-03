from playwright.async_api import Page

async def apply_stealth(page: Page):
    """Aplica configuraciones de modo sigiloso al navegador."""
    
    await page.add_init_script("""
        // Desactiva la detección de WebDriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });

        // Mockea funciones de detección de plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });

        // Mockea la propiedad languages para evitar detección
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });

        // Mockea la detección de la plataforma del navegador
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32',
        });

        // Mockear la detección del headless en userAgent
        Object.defineProperty(navigator, 'userAgent', {
            get: () => navigator.userAgent.replace('Headless', ''),
        });

        // Deshabilitar la detección de ad-blocker
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
            Promise.resolve({ state: 'denied' }) :
            originalQuery(parameters)
        );
    """)

    # Asegura que el viewport sea detectable correctamente
    await page.set_viewport_size({"width": 1366, "height": 768})
    print("Modo sigiloso aplicado")
