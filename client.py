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
            # Avviamo il browser simulando un utente reale
            browser = p.chromium.launch(headless=True) 
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
            page = context.new_page()

            print(f"🌐 Caricamento pagina di gioco...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # Aspettiamo che il gioco carichi i campi di testo
                page.wait_for_selector('input[type="email"]', timeout=15000)
                
                print(f"⌨️ Inserimento credenziali per {email}...")
                page.fill('input[type="email"]', email)
                time.sleep(1) # Pausa umana
                page.fill('input[type="password"]', password)
                time.sleep(1)
                
                print("🖱️ Click sul tasto Login...")
                # Cerchiamo il bottone di login specifico
                page.click('button[type="submit"], .login-button, button:has-text("Login")')

                print("⏳ Attesa generazione SessionID dal server...")
                # Aspettiamo 15 secondi per dare tempo ai Blob e ai Token di arrivare
                time.sleep(15)

                # Controlliamo i cookie per trovare il sessionID
                cookies = context.cookies()
                session_id = next((c['value'] for c in cookies if c['name'] == 'sessionID'), None)

                if session_id:
                    print(f"✅ SESSIONE AGGANCIATA: {session_id[:8]}...")
                    return RePanzaClient(session_id)
                
            except Exception as e:
                print(f"💥 Errore durante l'interazione: {e}")
            
            browser.close()
            return None
