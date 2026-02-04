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
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Fase Login
                page.wait_for_selector('input[placeholder="Email"]', timeout=20000)
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                print("🖱️ Click sul tasto LOG IN...")
                page.click('button:has-text("LOG IN")')
                
                # 2. Fase Selezione Mondo
                print("⏳ Attesa caricamento lista mondi...")
                # Aspettiamo che appaia il testo "Italia VI" che vediamo nello screenshot
                page.wait_for_selector('text="Italia VI"', timeout=30000)
                
                print("🏰 Selezione Mondo: Italia VI (IT)...")
                # Clicchiamo esattamente sulla riga del mondo
                page.click('text="Italia VI"')
                
                # Aspettiamo il caricamento del gioco vero e proprio
                print("⏳ Entrata nel mondo in corso...")
                time.sleep(15)

                # 3. Estrazione Sessione
                cookies = context.cookies()
                sid = next((c['value'] for c in cookies if c['name'] == 'sessionID'), None)
                
                if not sid:
                    sid = page.evaluate("localStorage.getItem('sessionID')")

                if sid:
                    print(f"✅ SESSIONE AGGANCIATA: {sid[:8]}...")
                    return RePanzaClient(sid)
                
                page.screenshot(path="debug_after_world_select.png")
                print("❌ Mondo selezionato ma sessione non trovata.")
                
            except Exception as e:
                print(f"💥 Errore durante la navigazione: {e}")
                page.screenshot(path="debug_error.png")
            
            browser.close()
            return None
