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

            auth_data = {"sid": None, "token": None}

            # Funzione per "leggere" dentro i file della tab Network
            def handle_response(response):
                if "login" in response.url and response.status == 200:
                    print(f"📡 File 'login' intercettato! Analisi contenuto...")
                    # 1. Cerchiamo negli Header (i Response Cookies che vedi tu)
                    headers = response.all_headers()
                    cookie_str = headers.get("set-cookie", "")
                    
                    sid_match = re.search(r'sessionID=([a-z0-9\-]+)', cookie_str)
                    token_match = re.search(r'token=([a-z0-9\-]+)', cookie_str)
                    
                    if sid_match: auth_data["sid"] = sid_match.group(1)
                    if token_match: auth_data["token"] = token_match.group(1)

            page.on("response", handle_response)

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # Login
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # Selezione Mondo
                time.sleep(12)
                print("🎯 Selezione Italia VI per forzare il file login...")
                page.mouse.click(300, 230)
                
                # Aspettiamo la cattura
                for _ in range(20):
                    if auth_data["sid"]: break
                    time.sleep(1)

                if auth_data["sid"]:
                    print(f"✅ SESSIONE TROVATA: {auth_data['sid'][:8]}...")
                    # Salvataggio immediato su file per non perderlo
                    with open("session_data.txt", "w") as f:
                        f.write(f"SID={auth_data['sid']}\nTOKEN={auth_data['token']}")
                    return RePanzaClient(auth_data["sid"], auth_data["token"])
                
                print("❌ Il file login non ha mostrato i dati negli header.")
                # Facciamo uno screenshot per vedere cosa vede il bot ora
                page.screenshot(path="debug_final_view.png")
                
            except Exception as e:
                print(f"💥 Errore: {e}")
            
            browser.close()
            return None
