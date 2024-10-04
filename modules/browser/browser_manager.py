from playwright.async_api import async_playwright

class BrowserManager:
    def __init__(self, executable_path, headless=True, storage_state=None):
        self.executable_path = executable_path
        self.headless = headless
        self.storage_state = storage_state
        self.browser = None
        self.context = None
        self.playwright = None

    async def start_browser(self):
        try:
            if not self.playwright:
                self.playwright = await async_playwright().start()

            if not self.browser:
                self.browser = await self.playwright.chromium.launch(executable_path=self.executable_path, headless=self.headless)
                self.context = await self.browser.new_context(storage_state=self.storage_state, accept_downloads=True)

            if not self.browser:
                raise Exception("Failed to launch the browser.")

        except Exception as e:
            print(f"Error launching browser: {e}")
            self.browser = None  # Asegúrate de que el navegador se limpie si no se inicia

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
