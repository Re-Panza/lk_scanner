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
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=5)
            except:
                pass

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()
            
            # Usiamo un dizionario mutabile per condividere i dati tra i thread
            capture = {"sid": None}

            def intercept_response(response):
                # Cerchiamo il pacchetto login (o loginAction)
                if "login" in response.url and response.status == 200:
                    try:
                        cookies = context.cookies()
                        for cookie in cookies:
                            if cookie['name'] == 'sessionID':
                                capture["sid"] = cookie['value']
                                # Non stampiamo qui per non sporcare il log, lo fa il main loop
                    except:
                        pass

            page.on("response", intercept_response)
            
            try:
                print("🌐 Caricamento Lords & Knights...")
                # Timeout aumentato per connessioni lente
                page.goto("https://www.lordsandknights.com/", wait_until="networkidle", timeout=90000)
                
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                selector_mondo = ".button-game-world--title:has-text('Italia VI')"
                print("⏳ Attesa comparsa mondi...")
                page.wait_for_selector(selector_mondo, timeout=30000)
                
                print("🎯 Click su Italia VI...")
                # Doppio metodo di click per massima sicurezza
                page.locator(selector_mondo).first.click(force=True)
                page.locator(selector_mondo).first.evaluate("node => node.click()")

                # CICLO DI ATTESA (fino a 90 secondi)
                print("📡 In ascolto per il sessionID...")
                for i in range(90):
                    # CONTROLLO VITTORIA: Se abbiamo il SID, usciamo subito!
                    if capture["sid"]:
                        sid_final = capture["sid"]
                        print(f"✅ SID CATTURATO AL SECONDO {i}: {sid_final[:10]}...")
                        browser.close()
                        return RePanzaClient(sid_final)
                    
                    time.sleep(1)
                    if i % 10 == 0 and i > 0:
                        print(f"   ...attesa {i}s ...")
                
                print("❌ Timeout: SID non arrivato in 90 secondi.")
                page.screenshot(path="debug_timeout.png")
                
            except Exception as e:
                print(f"⚠️ Errore nel processo: {e}")
            
            browser.close()
            return None
