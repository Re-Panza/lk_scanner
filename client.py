from playwright.sync_api import sync_playwright
import time
import os
import requests

class RePanzaClient:
    def __init__(self, session_id, cookies, user_agent):
        self.session_id = session_id
        self.cookies = cookies
        self.user_agent = user_agent

    @staticmethod
    def send_telegram_alert(message):
        token = os.getenv("TELEGRAM_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if token and chat_id:
            try:
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                            data={"chat_id": chat_id, "text": message}, timeout=5)
            except: pass

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            # TORNIAMO AL DESKTOP: Questo garantisce che il sito carichi i bottoni giusti
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720}, user_agent=ua)
            page = context.new_page()
            
            capture = {"sid": None}

            def intercept_response(response):
                if "login" in response.url and response.status == 200:
                    try:
                        cookies = context.cookies()
                        for c in cookies:
                            if c['name'] == 'sessionID':
                                capture["sid"] = c['value']
                    except: pass

            page.on("response", intercept_response)
            
            try:
                print("🌐 Caricamento Lords & Knights (Modalità Desktop)...")
                page.goto("https://www.lordsandknights.com/", wait_until="networkidle", timeout=90000)
                
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                selector_mondo = page.locator(".button-game-world--title:has-text('Italia VI')").first
                selector_ok = page.locator("button:has-text('OK')")
                
                print("⏳ Attesa accesso mondo...")
                for i in range(120): # 2 minuti di tentativi
                    # 1. Manutenzione
                    if selector_ok.is_visible():
                        print("🛠️ Premo OK su Manutenzione...")
                        selector_ok.click()
                        time.sleep(1)
                    
                    # 2. Ingresso Mondo
                    if selector_mondo.is_visible():
                        print("🎯 Trovato Italia VI! Entro...")
                        selector_mondo.click(force=True)
                        selector_mondo.evaluate("node => node.click()")
                    
                    # 3. Controllo Successo
                    if capture["sid"]:
                        all_cookies = context.cookies()
                        sid_final = capture["sid"]
                        print(f"✅ Login Successo! Catturati {len(all_cookies)} cookie.")
                        browser.close()
                        return RePanzaClient(sid_final, all_cookies, ua)
                    
                    time.sleep(1)
                    
                # SE ARRIVIAMO QUI, È TIMEOUT -> FACCIO LA FOTO
                print("❌ Timeout Login! Salvo screenshot di debug...")
                page.screenshot(path="debug_timeout.png")
                
            except Exception as e:
                print(f"⚠️ Errore Login: {e}")
                try:
                    page.screenshot(path="debug_error.png")
                except: pass
            
            browser.close()
            return None
