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
            try:
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                            data={"chat_id": chat_id, "text": message}, timeout=5)
            except Exception as e:
                print(f"⚠️ Errore Telegram: {e}")

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()
            capture = {"sid": None}

            def intercept_response(response):
                if "login" in response.url and response.status == 200:
                    try:
                        cookies = context.cookies()
                        for c in cookies:
                            if c['name'] == 'sessionID':
                                capture["sid"] = c['value']
                                print(f"✅ SID INTERCETTATO: {capture['sid'][:10]}...")
                    except: pass

            page.on("response", intercept_response)
            
            try:
                print("🌐 Caricamento Lords & Knights...")
                page.goto("https://www.lordsandknights.com/", wait_until="networkidle", timeout=90000)
                
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # Locator specifici per evitare conflitti
                selector_mondo = page.locator(".button-game-world--title:has-text('Italia VI')").first
                selector_ok = page.locator("button:has-text('OK')")
                
                for i in range(120):
                    if selector_ok.is_visible():
                        print("🛠️ Manutenzione rilevata. Premo OK...")
                        selector_ok.click()
                        time.sleep(2)
                    
                    if selector_mondo.is_visible():
                        print("🎯 Italia VI trovato. Entro...")
                        selector_mondo.click(force=True)
                        selector_mondo.evaluate("node => node.click()")
                    
                    if capture["sid"]:
                        sid_final = capture["sid"]
                        browser.close()
                        return RePanzaClient(sid_final)
                    
                    time.sleep(1)
            except Exception as e:
                print(f"⚠️ Errore: {e}")
            
            browser.close()
            return None
