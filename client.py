from playwright.sync_api import sync_playwright
import time
import re

class RePanzaClient:
    def __init__(self, session_id, token):
        self.session_id = session_id
        self.token = token

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Login
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                
                # Prepariamo l'ascoltatore per la risposta del server prima di cliccare
                with page.expect_response(lambda response: "login" in response.url and response.status == 200, timeout=60000) as response_info:
                    page.click('button:has-text("LOG IN")')
                    
                    # Dopo il login, clicchiamo sul mondo per forzare la sessione finale
                    time.sleep(10)
                    print("🎯 Selezione Italia VI...")
                    page.mouse.click(300, 230)
                
                # 2. Analisi della risposta intercettata
                response = response_info.value
                headers = response.all_headers()
                cookie_str = headers.get("set-cookie", "")
                
                print(f"📡 Analisi risposta login completata. Cerco SID e Token...")
                
                sid_match = re.search(r'sessionID=([a-z0-9\-]+)', cookie_str)
                token_match = re.search(r'token=([a-z0-9\-]+)', cookie_str)
                
                sid = sid_match.group(1) if sid_match else None
                token = token_match.group(1) if token_match else None

                if sid:
                    print(f"✅ SESSIONE AGGANCIATA: {sid[:8]}...")
                    with open("session_data.txt", "w") as f:
                        f.write(f"SID={sid}\nTOKEN={token}")
                    return RePanzaClient(sid, token)
                
                print("❌ Dati non trovati nella risposta del server.")
                page.screenshot(path="debug_network_fail.png")
                
            except Exception as e:
                print(f"💥 Errore durante l'intercettazione: {e}")
            
            browser.close()
            return None
