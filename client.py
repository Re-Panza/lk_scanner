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
                # 1. Login veloce
                page.wait_for_selector('input[placeholder="Email"]', timeout=15000)
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # 2. Selezione Mondo "Senza Esitazione"
                print("🏰 Cerco Italia VI per il click...")
                
                # Usiamo un selettore più potente che cerca il testo dentro i contenitori dei mondi
                world_selector = 'text="Italia VI"'
                page.wait_for_selector(world_selector, timeout=20000)
                
                # Forziamo il click anche se Playwright pensa che sia coperto o non visibile
                page.click(world_selector, force=True, timeout=5000)
                print("🖱️ Click su Italia VI inviato!")
                
                # 3. Cattura Sessione
                print("⏳ Entrata nel mondo...")
                time.sleep(15)

                cookies = context.cookies()
                sid = next((c['value'] for c in cookies if c['name'] == 'sessionID'), None)
                
                if not sid:
                    sid = page.evaluate("localStorage.getItem('sessionID')")

                if sid:
                    print(f"✅ SESSIONE AGGANCIATA: {sid[:8]}...")
                    return RePanzaClient(sid)
                
                page.screenshot(path="debug_after_click_world.png")
                print("❌ Click fatto ma sessione non rilevata.")
                
            except Exception as e:
                print(f"💥 Errore: {e}")
                page.screenshot(path="debug_final_error.png")
            
            browser.close()
            return None
