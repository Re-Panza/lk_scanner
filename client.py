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
            # Usiamo una finestra 1280x720 come quella dello screenshot
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # Aspettiamo che la maschera di login sia pronta
                print("⏳ Localizzazione campi di login in alto a destra...")
                
                # Usiamo i placeholder che vediamo nell'immagine: "Email" e "Password"
                page.wait_for_selector('input[placeholder="Email"]', timeout=20000)
                
                print(f"⌨️ Scrittura credenziali...")
                # Forziamo il click prima di scrivere per essere sicuri di avere il focus
                page.click('input[placeholder="Email"]')
                page.type('input[placeholder="Email"]', email, delay=100)
                
                page.click('input[placeholder="Password"]')
                page.type('input[placeholder="Password"]', password, delay=100)
                
                print("🖱️ Click sul tasto LOG IN arancione...")
                # Puntiamo al tasto LOG IN che vediamo nello screenshot
                page.click('button:has-text("LOG IN"), .login-button, .button-login')

                print("⏳ Attesa validazione (15s)...")
                time.sleep(15)

                # Estrazione sessione dai cookie
                cookies = context.cookies()
                session_id = next((c['value'] for c in cookies if c['name'] == 'sessionID'), None)

                if session_id:
                    print(f"✅ SESSIONE CATTURATA: {session_id[:8]}...")
                    return RePanzaClient(session_id)
                
                # Se non trova il cookie, facciamo un altro screenshot per vedere cosa è successo dopo il click
                page.screenshot(path="debug_after_click.png")
                print("❌ Login premuto ma sessione non trovata. Screenshot salvato.")
                
            except Exception as e:
                page.screenshot(path="debug_login.png")
                print(f"💥 Errore durante l'inserimento: {e}")
            
            browser.close()
            return None
