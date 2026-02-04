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
            # Manteniamo la risoluzione fissa dello screenshot
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Login
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # 2. Attesa caricamento lista mondi
                print("⏳ Attesa comparsa schermata mondi (12s)...")
                time.sleep(12)
                
                # 3. CLICK A COORDINATE CORRETTE
                # Basandoci sullo screenshot, il box di Italia VI è largo. 
                # Proviamo un punto più centrale nel box: X=300, Y=230
                print("🎯 Lancio click balistico su Italia VI (X:300, Y:230)...")
                
                # Muoviamo prima il mouse (simula l'hover) e poi clicchiamo
                page.mouse.move(300, 230)
                time.sleep(1)
                page.mouse.click(300, 230)
                
                print("🖱️ Click inviato!")
                
                # 4. Verifica Sessione
                print("⏳ Entrata nel mondo...")
                time.sleep(15)

                cookies = context.cookies()
                sid = next((c['value'] for c in cookies if c['name'] == 'sessionID'), None)
                
                if sid:
                    print(f"✅ SESSIONE AGGANCIATA: {sid[:8]}...")
                    return RePanzaClient(sid)
                
                # Salviamo uno screenshot per capire dove ha cliccato effettivamente
                page.screenshot(path="debug_mouse_click.png")
                print("❌ Sessione non trovata. Controlla debug_mouse_click.png")
                
            except Exception as e:
                print(f"💥 Errore: {e}")
                page.screenshot(path="debug_error.png")
            
            browser.close()
            return None
