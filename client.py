from playwright.sync_api import sync_playwright
import time
import re

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            auth_data = {"sid": None}

            # Sniffer per intercettare il pacchetto login.xhr
            def intercept_response(response):
                if "login" in response.url and response.status == 200:
                    # Controlliamo i cookie nel contesto
                    cookies = context.cookies()
                    for cookie in cookies:
                        if cookie['name'] == 'sessionID':
                            auth_data["sid"] = cookie['value']

            page.on("response", intercept_response)

            print("🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # Login
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # Selezione Mondo con il selettore che abbiamo trovato
                selector_mondo = ".button-game-world--title:has-text('Italia VI')"
                page.wait_for_selector(selector_mondo, timeout=30000)
                print("🎯 Click su Italia VI...")
                page.locator(selector_mondo).first.click(force=True)
                
                # Attesa cattura
                for _ in range(30):
                    if auth_data["sid"]:
                        print(f"✅ SESSIONE CATTURATA: {auth_data['sid'][:10]}...")
                        browser.close()
                        return RePanzaClient(auth_data["sid"])
                    time.sleep(1)
                
            except Exception as e:
                print(f"💥 Errore nel client: {e}")
            
            browser.close()
            return None
