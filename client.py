from playwright.sync_api import sync_playwright
import time
import os
import requests

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id

    @staticmethod
    def send_telegram_alert(message):
        token = os.getenv("TELEGRAM_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            try:
                requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
            except:
                pass

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()
            auth_data = {"sid": None}

            def intercept_response(response):
                if "login" in response.url:
                    if response.status == 200:
                        try:
                            # Cattura SID dai cookie
                            cookies = context.cookies()
                            for cookie in cookies:
                                if cookie['name'] == 'sessionID':
                                    auth_data["sid"] = cookie['value']
                        except:
                            pass

            page.on("response", intercept_response)
            
            print("🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle", timeout=60000)
            
            try:
                # Login
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # Attesa stabilizzazione pagina mondi
                print("⏳ Attesa comparsa mondi...")
                selector_mondo = ".button-game-world--title:has-text('Italia VI')"
                page.wait_for_selector(selector_mondo, timeout=30000)
                
                # Doppio tentativo di click per sicurezza
                print("🎯 Click su Italia VI...")
                page.locator(selector_mondo).first.click(force=True)
                time.sleep(2)
                if not auth_data["sid"]:
                    page.locator(selector_mondo).first.dispatch_event("click")

                # Loop di attesa rinforzato
                for i in range(45):
                    if auth_data["sid"]:
                        sid_final = auth_data["sid"]
                        print(f"✅ Sessione agganciata: {sid_final[:10]}")
                        browser.close()
                        return RePanzaClient(sid_final)
                    if i % 10 == 0 and i > 0:
                        print("🔄 Ancora in attesa del pacchetto login.xhr...")
                    time.sleep(1)
            
            except Exception as e:
                print(f"⚠️ Errore durante la sequenza: {e}")
            
            browser.close()
            return None
