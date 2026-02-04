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
            
            # Usiamo un dizionario per condividere il dato tra le funzioni
            state = {"sid": None}

            def intercept_response(response):
                if "login" in response.url and response.status == 200:
                    try:
                        cookies = context.cookies()
                        for cookie in cookies:
                            if cookie['name'] == 'sessionID':
                                state["sid"] = cookie['value']
                                print(f"✅ SID INTERCETTATO: {state['sid'][:8]}...")
                    except:
                        pass

            page.on("response", intercept_response)
            
            try:
                print("🌐 Caricamento Lords & Knights...")
                page.goto("https://www.lordsandknights.com/", wait_until="networkidle", timeout=60000)
                
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                selector_mondo = ".button-game-world--title:has-text('Italia VI')"
                page.wait_for_selector(selector_mondo, timeout=30000)
                
                print("🎯 Click su Italia VI...")
                world_button = page.locator(selector_mondo).first
                world_button.click(force=True)
                
                # Secondo click di rinforzo via JS per velocizzare il server
                world_button.evaluate("node => node.click()")

                # Aspettiamo fino a 60 secondi, ma usciamo appena abbiamo il SID
                for i in range(60):
                    if state["sid"]:
                        sid_final = state["sid"]
                        browser.close()
                        return RePanzaClient(sid_final)
                    time.sleep(1)
                
                print("❌ Timeout scaduto prima della cattura.")
                page.screenshot(path="debug_timeout.png")
                
            except Exception as e:
                print(f"⚠️ Errore: {e}")
            
            browser.close()
            return None
