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
            # Browser con finestra fissa 1280x720
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Login veloce
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # 2. Attesa caricamento lista mondi
                print("⏳ Attesa comparsa schermata mondi (10s)...")
                time.sleep(10)
                
                # 3. CLICK A COORDINATE ESATTE (Bypass visibilità)
                # Nello screenshot 1280x720, Italia VI è nel primo box in alto a sinistra.
                # X: 150 (leggermente a destra del margine), Y: 230 (altezza del primo box)
                print("🎯 Lancio click balistico su coordinate X:150, Y:230...")
                page.mouse.click(150, 230)
                
                # Proviamo anche un secondo click leggermente più in basso per sicurezza
                time.sleep(1)
                page.mouse.click(150, 250)
                
                print("🖱️ Click inviati fisicamente alla zona 'Italia VI'!")
                
                # 4. Verifica Sessione
                print("⏳ Entrata nel mondo...")
                time.sleep(15)

                cookies = context.cookies()
                sid = next((c['value'] for c in cookies if c['name'] == 'sessionID'), None)
                
                if sid:
                    print(f"✅ SESSIONE CATTURATA: {sid[:8]}...")
                    return RePanzaClient(sid)
                
                # Screenshot per vedere se il mouse ha colpito il punto giusto
                page.screenshot(path="debug_mouse_click.png")
                print("❌ Il click alle coordinate non ha generato una sessione.")
                
            except Exception as e:
                print(f"💥 Errore tecnico: {e}")
                page.screenshot(path="debug_crash.png")
            
            browser.close()
            return None
