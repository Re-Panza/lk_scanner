from playwright.sync_api import sync_playwright
import time
import json

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

            auth_data = {"sessionID": None, "token": None}

            # Intercettiamo il contenuto del file 'login'
            def handle_response(response):
                if "login" in response.url and response.status == 200:
                    try:
                        # Molte info di L&K sono in JSON o passate negli header di risposta
                        # Estraiamo i dati direttamente come farebbero i DevTools
                        headers = response.all_headers()
                        set_cookies = headers.get("set-cookie", "")
                        
                        if "sessionID=" in set_cookies:
                            auth_data["sessionID"] = set_cookies.split("sessionID=")[1].split(";")[0]
                        if "token=" in set_cookies:
                            auth_data["token"] = set_cookies.split("token=")[1].split(";")[0]
                            
                        if auth_data["sessionID"]:
                            print(f"✅ DATI LOGIN CAPTURATI: {auth_data['sessionID'][:8]}...")
                    except Exception as e:
                        print(f"⚠️ Errore decodifica login: {e}")

            page.on("response", handle_response)

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Login
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # 2. Click Mondo
                time.sleep(12)
                print("🎯 Selezione Italia VI...")
                page.mouse.click(300, 230)
                
                # 3. Attesa cattura dati (massimo 20 secondi)
                for _ in range(20):
                    if auth_data["sessionID"]:
                        break
                    time.sleep(1)

                if auth_data["sessionID"]:
                    with open("session_data.txt", "w") as f:
                        f.write(f"SID={auth_data['sessionID']}\nTOKEN={auth_data['token']}")
                    return RePanzaClient(auth_data["sessionID"], auth_data["token"])
                
                print("❌ Il file 'login' non ha fornito i dati necessari.")
                page.screenshot(path="debug_final.png")
                
            except Exception as e:
                print(f"💥 Errore tecnico: {e}")
            
            browser.close()
            return None
