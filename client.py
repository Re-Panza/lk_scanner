from playwright.sync_api import sync_playwright
import time

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

            # Variabili per salvare i dati estratti dal "file" login
            auth_data = {"sessionID": None, "token": None}

            # Funzione che "legge" le risposte proprio come nei DevTools
            def intercept_response(response):
                # Cerchiamo la chiamata 'login' che hai evidenziato
                if "login" in response.url and response.status == 200:
                    try:
                        # Estraiamo i cookie direttamente dalla risposta del server
                        cookies = response.headers_array()
                        for cookie in cookies:
                            if cookie['name'].lower() == 'set-cookie':
                                value = cookie['value']
                                if 'sessionID=' in value:
                                    auth_data["sessionID"] = value.split('sessionID=')[1].split(';')[0]
                                if 'token=' in value:
                                    auth_data["token"] = value.split('token=')[1].split(';')[0]
                        
                        if auth_data["sessionID"]:
                            print(f"✅ Dati intercettati dal file login: {auth_data['sessionID'][:8]}...")
                    except Exception as e:
                        print(f"⚠️ Errore lettura risposta: {e}")

            # Attiviamo lo sniffer di risposte
            page.on("response", intercept_response)

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Login
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # 2. Click su Italia VI per scatenare la creazione della sessione
                time.sleep(10)
                page.mouse.click(300, 230)
                
                # Aspettiamo che il server risponda con il file 'login'
                print("⏳ In attesa della risposta dal server (file login)...")
                for _ in range(20):
                    if auth_data["sessionID"] and auth_data["token"]:
                        break
                    time.sleep(1)

                if auth_data["sessionID"]:
                    print(f"✅ VITTORIA: Sessione e Token catturati con successo!")
                    # Salvataggio per uso futuro
                    with open("session_data.txt", "w") as f:
                        f.write(f"SID={auth_data['sessionID']}\nTOKEN={auth_data['token']}")
                    return RePanzaClient(auth_data["sessionID"], auth_data["token"])
                
                print("❌ Il server non ha inviato i dati di sessione nel tempo previsto.")
                page.screenshot(path="debug_no_login_data.png")
                
            except Exception as e:
                print(f"💥 Errore: {e}")
            
            browser.close()
            return None
