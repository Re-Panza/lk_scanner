from playwright.sync_api import sync_playwright
import time
import json

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            captured_data = {"sid": None}

            # Questa funzione legge il contenuto del file 'login' proprio come nei DevTools
            def handle_response(response):
                if "login" in response.url and response.status == 200:
                    try:
                        # Estraiamo il JSON della risposta
                        text = response.text()
                        if "sessionID" in text:
                            # Cerchiamo il valore con una ricerca testuale semplice per massima compatibilità
                            import re
                            match = re.search(r'sessionID["\s:]+([a-z0-9\-]+)', text)
                            if match:
                                captured_data["sid"] = match.group(1)
                                print(f"📡 SESSIONE INTERCETTATA DAL PAYLOAD: {captured_data['sid'][:8]}...")
                    except:
                        pass

            page.on("response", handle_response)

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Login
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # 2. Selezione Mondo Italia VI
                time.sleep(10)
                print("🎯 Selezione Italia VI...")
                page.mouse.click(300, 230)
                
                # Aspettiamo che il server invii il file 'login'
                print("⏳ In attesa del payload di sessione...")
                for _ in range(20):
                    if captured_data["sid"]:
                        break
                    time.sleep(1)

                if captured_data["sid"]:
                    print(f"✅ VITTORIA! SessionID catturato con successo.")
                    with open("session_data.txt", "w") as f:
                        f.write(f"SID={captured_data['sid']}")
                    return RePanzaClient(captured_data["sid"])
                
                print("❌ Il payload JSON non conteneva il sessionID.")
                page.screenshot(path="debug_network_payload.png")
                
            except Exception as e:
                print(f"💥 Errore: {e}")
            
            browser.close()
            return None
