from playwright.sync_api import sync_playwright
import os
import time

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        self.base_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Usiamo un'identità più simile a un browser desktop per evitare il blocco "Connect with Facebook"
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Inserimento credenziali
                page.wait_for_selector('input[placeholder="Email"]', timeout=20000)
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                
                # 2. Click e attesa navigazione
                print("🖱️ Click sul tasto LOG IN e attesa risposta server...")
                page.click('button:has-text("LOG IN")')
                
                # Aspettiamo che il caricamento finisca (il gioco è pesante)
                time.sleep(20) 

                # 3. Controllo Sessione in vari posti (Cookie o LocalStorage)
                cookies = context.cookies()
                # Cerchiamo il cookie sessionID
                sid = next((c['value'] for c in cookies if c['name'] == 'sessionID'), None)
                
                # Se non è nei cookie, potrebbe essere nel LocalStorage del browser
                if not sid:
                    sid = page.evaluate("localStorage.getItem('sessionID')")

                if sid:
                    print(f"✅ SESSIONE AGGANCIATA: {sid[:8]}...")
                    return RePanzaClient(sid)
                
                # Se fallisce ancora, salviamo cosa vede il bot dopo il login
                page.screenshot(path="debug_after_login_attempt.png")
                print("❌ Sessione non trovata dopo 20s. Forse serve un secondo click?")
                
            except Exception as e:
                print(f"💥 Errore: {e}")
                page.screenshot(path="debug_login_error.png")
            
            browser.close()
            return None
