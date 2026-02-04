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

            auth_result = {"sid": None}

            # Funzione mirata sul pacchetto login.xhr
            def intercept_xhr(response):
                # Cerchiamo specificamente il file login o le chiamate XHR di login
                if "login" in response.url and response.status == 200:
                    print(f"📡 Intercettato pacchetto: {response.url}")
                    
                    # Estraiamo gli header di risposta (dove stanno i Response Cookies)
                    headers = response.all_headers()
                    set_cookie = headers.get("set-cookie", "")
                    
                    # Se il sessionID è qui dentro, lo prendiamo con la regex
                    if "sessionID=" in set_cookie:
                        match = re.search(r'sessionID=([a-z0-9\-]+)', set_cookie)
                        if match:
                            auth_result["sid"] = match.group(1)
                            print(f"✅ sessionID estratto da login.xhr: {auth_result['sid'][:8]}...")

            # Attiviamo lo sniffer prima delle azioni
            page.on("response", intercept_xhr)

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Login
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # 2. Selezione Mondo (scatena il login.xhr)
                time.sleep(10)
                print("🎯 Selezione Mondo per scatenare login.xhr...")
                page.mouse.click(300, 230) 
                
                # 3. Attesa cattura dati
                for _ in range(25):
                    if auth_result["sid"]:
                        break
                    time.sleep(1)

                if auth_result["sid"]:
                    print(f"🎉 VITTORIA! Sessione recuperata dal pacchetto XHR.")
                    with open("session_data.txt", "w") as f:
                        f.write(f"SID={auth_result['sid']}")
                    return RePanzaClient(auth_result["sid"])
                
                print("❌ Il pacchetto login.xhr è passato ma non conteneva il sessionID negli header.")
                page.screenshot(path="debug_xhr_fail.png")
                
            except Exception as e:
                print(f"💥 Errore: {e}")
            
            browser.close()
            return None
