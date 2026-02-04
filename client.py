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
                if "login" in response.url and response.status == 200:
                    try:
                        cookies = context.cookies()
                        for cookie in cookies:
                            if cookie['name'] == 'sessionID':
                                auth_data["sid"] = cookie['value']
                                print(f"✅ SID intercettato: {auth_data['sid'][:8]}...")
                    except:
                        pass

            page.on("response", intercept_response)
            
            try:
                print("🌐 Caricamento Lords & Knights...")
                page.goto("https://www.lordsandknights.com/", wait_until="networkidle", timeout=60000)
                
                # Inserimento credenziali
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # Attesa della lista mondi
                selector_mondo = ".button-game-world--title:has-text('Italia VI')"
                print("⏳ Attesa comparsa mondi...")
                page.wait_for_selector(selector_mondo, timeout=30000)
                
                # Click forzato e ripetuto
                print("🎯 Click su Italia VI...")
                world_button = page.locator(selector_mondo).first
                world_button.click(force=True)
                time.sleep(3)
                
                # Se non ha ancora il SID, prova il click via JavaScript
                if not auth_data["sid"]:
                    print("🔄 Tentativo click JavaScript...")
                    world_button.evaluate("node => node.click()")

                # Loop di attesa finale
                for i in range(30):
                    if auth_data["sid"]:
                        sid_final = auth_data["sid"]
                        browser.close()
                        return RePanzaClient(sid_final)
                    if i % 5 == 0:
                        print(f"📡 In attesa del pacchetto... ({i}s)")
                    time.sleep(1)
                
                # Se fallisce, salva lo screenshot per capire perché
                print("❌ Fallimento. Salvo screenshot di debug...")
                page.screenshot(path="debug_login_error.png")
                
            except Exception as e:
                print(f"⚠️ Errore critico: {e}")
                page.screenshot(path="debug_crash.png")
            
            browser.close()
            return None
