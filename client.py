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
            # Avvio browser con risoluzione fissa come lo screenshot
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="domcontentloaded")
            
            try:
                # 1. Login Rapido
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # 2. Click Forzato su Italia VI
                print("🏰 Tentativo di click su Italia VI...")
                
                # Aspettiamo solo 5 secondi che il testo appaia nel codice
                page.wait_for_selector('text="Italia VI"', timeout=5000)
                
                # Clicchiamo usando il metodo 'dispatch_event' che simula il click 
                # a livello di codice, scavalcando i controlli di visibilità
                page.locator('text="Italia VI"').dispatch_event("click")
                
                print("🖱️ Segnale di click inviato a Italia VI!")
                
                # 3. Recupero Sessione
                print("⏳ Entrata nel mondo...")
                time.sleep(15)

                cookies = context.cookies()
                sid = next((c['value'] for c in cookies if c['name'] == 'sessionID'), None)
                
                if sid:
                    print(f"✅ SESSIONE AGGANCIATA: {sid[:8]}...")
                    return RePanzaClient(sid)
                
                # Se fallisce, scattiamo l'ultimo screenshot di questa fase
                page.screenshot(path="debug_click_mondo.png")
                print("❌ Sessione non trovata dopo il click forzato.")
                
            except Exception as e:
                print(f"💥 Errore durante il click: {e}")
                page.screenshot(path="debug_final.png")
            
            browser.close()
            return None
