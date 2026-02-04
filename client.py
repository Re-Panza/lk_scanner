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
                # 1. Login
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # 2. Selezione Mondo (Mira confermata X:300, Y:230)
                print("⏳ Attesa schermata mondi...")
                time.sleep(12)
                page.mouse.click(300, 230)
                print("🖱️ Click su Italia VI inviato!")
                
                # 3. Attesa Caricamento Gioco
                print("🏰 Entrata nel castello... Attesa caricamento mappa (25s)...")
                # Aumentiamo l'attesa perché la mappa è pesante
                time.sleep(25) 
                
                # Facciamo uno screenshot della mappa per conferma
                page.screenshot(path="debug_mappa_gioco.png")

                # 4. Estrazione Sessione Post-Caricamento
                print("🔑 Tentativo recupero sessione attiva...")
                cookies = context.cookies()
                sid = next((c['value'] for c in cookies if c['name'] == 'sessionID'), None)
                
                if sid:
                    print(f"✅ SESSIONE AGGANCIATA: {sid[:8]}...")
                    # Salviamo la sessione in un file locale per gli usi futuri del Brain
                    with open("session.txt", "w") as f:
                        f.write(sid)
                    return RePanzaClient(sid)
                
                print("❌ Mappa caricata ma sessione non trovata nei cookie.")
                
            except Exception as e:
                print(f"💥 Errore: {e}")
                page.screenshot(path="debug_error.png")
            
            browser.close()
            return None
