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
            # Usiamo un'identità browser standard per evitare blocchi
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            page = context.new_page()

            print(f"🌐 Caricamento pagina...")
            # 'commit' è più veloce di 'networkidle' e previene i timeout sui caricamenti lenti
            page.goto("https://www.lordsandknights.com/", wait_until="commit")
            
            try:
                # Aspettiamo il selettore email con più pazienza (30 secondi)
                print("⏳ Cerco i campi di login (attesa max 30s)...")
                email_field = page.wait_for_selector('input[type="email"], input[name="login"]', timeout=30000)
                
                if email_field:
                    print(f"⌨️ Inserimento credenziali...")
                    page.fill('input[type="email"], input[name="login"]', email)
                    page.fill('input[type="password"]', password)
                    
                    # Clicchiamo il tasto login principale
                    page.click('button[type="submit"], .login-button')
                    
                    print("⏳ Login effettuato. Controllo sessione...")
                    time.sleep(10) # Tempo per il server di rispondere

                    cookies = context.cookies()
                    session_id = next((c['value'] for c in cookies if c['name'] == 'sessionID'), None)

                    if session_id:
                        print(f"✅ SESSIONE OK: {session_id[:8]}...")
                        return RePanzaClient(session_id)
                
            except Exception as e:
                # Se fallisce, facciamo uno screenshot per capire cosa vede il bot (verrà salvato su GitHub)
                page.screenshot(path="debug_login.png")
                print(f"💥 Timeout o elemento non trovato. Screenshot salvato come debug_login.png")
            
            browser.close()
            return None
