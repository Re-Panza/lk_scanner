from playwright.sync_api import sync_playwright
import time
import re

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        # URL base per le chiamate API di Italia VI
        self.base_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            # Avvio browser in modalità headless per GitHub Actions
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            # Variabile per salvare il SID catturato
            auth_data = {"sid": None}

            # --- SNIFFER DI RETE (Come la tab Network dei DevTools) ---
            def intercept_response(response):
                # Cerchiamo il pacchetto login che hai identificato
                if "login" in response.url and response.status == 200:
                    print(f"📡 Pacchetto intercettato: {response.url}")
                    
                    # 1. Prova a prenderlo dai Cookie di memoria (più affidabile)
                    cookies = context.cookies()
                    for cookie in cookies:
                        if cookie['name'] == 'sessionID':
                            auth_data["sid"] = cookie['value']
                            print(f"✅ SID estratto dai Cookie: {auth_data['sid'][:8]}...")
                    
                    # 2. Se non è nei cookie, lo cerchiamo negli Header di risposta
                    if not auth_data["sid"]:
                        headers = response.all_headers()
                        set_cookie = headers.get("set-cookie", "")
                        match = re.search(r'sessionID=([a-z0-9\-]+)', set_cookie)
                        if match:
                            auth_data["sid"] = match.group(1)
                            print(f"✅ SID estratto dagli Header: {auth_data['sid'][:8]}...")

            page.on("response", intercept_response)

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Fase di Login
                print("🔑 Inserimento credenziali...")
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # 2. Selezione del Mondo
                # Usiamo l'elemento HTML specifico che hai trovato
                selector_mondo = ".button-game-world--title:has-text('Italia VI')"
                print(f"⏳ Attesa comparsa: {selector_mondo}...")
                
                page.wait_for_selector(selector_mondo, timeout=30000)
                
                # Click forzato per bypassare eventuali blocchi grafici
                print("🎯 Click tecnico su Italia VI...")
                page.locator(selector_mondo).first.click(force=True)
                
                # 3. Attesa cattura dati (max 30 secondi)
                print("🏰 Entrata nel mondo... In ascolto per il sessionID...")
                for _ in range(30):
                    if auth_data["sid"]:
                        break
                    time.sleep(1)

                if auth_data["sid"]:
                    print(f"🎉 VITTORIA! Sessione recuperata.")
                    # Salviamo i dati per Re Panza Brain
                    with open("session_data.txt", "w") as f:
                        f.write(f"SID={auth_data['sid']}")
                    return RePanzaClient(auth_data["sid"])
                
                # Se fallisce, screenshot di debug
                print("❌ Sessione non intercettata. Salvo screenshot di controllo.")
                page.screenshot(path="debug_final_view.png")
                
            except Exception as e:
                print(f"💥 Errore tecnico: {e}")
                page.screenshot(path="debug_error_crash.png")
            
            browser.close()
            return None
