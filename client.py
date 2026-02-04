from playwright.sync_api import sync_playwright
import os
import time
import re

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

            # Variabile per salvare il sessionID intercettato
            captured_sid = {"id": None}

            # Funzione che analizza ogni richiesta di rete
            def handle_request(request):
                # Cerchiamo il sessionID nell'URL della richiesta (tipico dei cURL di L&K)
                if "sessionID=" in request.url:
                    match = re.search(r'sessionID=([a-z0-9\-]+)', request.url)
                    if match:
                        captured_sid["id"] = match.group(1)
                        print(f"📡 INTERCETTATO sessionID dalla rete: {captured_sid['id'][:8]}...")

            # Attiviamo lo sniffer di rete prima di fare qualsiasi cosa
            page.on("request", handle_request)

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Login
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # 2. Selezione Mondo (Coordinate X:300, Y:230)
                time.sleep(12)
                page.mouse.click(300, 230)
                print("🖱️ Click su Italia VI inviato!")
                
                # 3. Attesa Caricamento Gioco e Intercettazione
                print("🏰 Entrata nel castello... In ascolto per il sessionID (30s)...")
                
                # Aspettiamo che il gioco faccia le sue chiamate per caricare la mappa
                for _ in range(30):
                    if captured_sid["id"]:
                        break
                    time.sleep(1)

                if captured_sid["id"]:
                    print(f"✅ VITTORIA! Sessione catturata dal traffico: {captured_sid['id'][:8]}...")
                    return RePanzaClient(captured_sid["id"])
                
                # Se fallisce, facciamo lo screenshot della mappa per vedere se siamo dentro
                page.screenshot(path="debug_mappa_gioco.png")
                print("❌ Mappa caricata ma nessun sessionID passato nei cURL di rete.")
                
            except Exception as e:
                print(f"💥 Errore: {e}")
            
            browser.close()
            return None
