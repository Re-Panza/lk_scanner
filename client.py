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
            # Riproduciamo esattamente l'ambiente dove vedi i cookie
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Login Rapido
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # 2. Selezione Mondo Italia VI
                print("⏳ Attesa caricamento mondi...")
                time.sleep(10)
                page.mouse.click(300, 230)
                print("🖱️ Click su Italia VI inviato!")
                
                # 3. Recupero immediato dei Cookie
                # Aspettiamo solo qualche secondo per permettere al server di rispondere con i Set-Cookie
                print("⏳ Recupero dati di sessione in corso...")
                time.sleep(10) 

                cookies = context.cookies()
                
                # Cerchiamo i tre valori chiave che vediamo nei tuoi DevTools
                sid = next((c['value'] for c in cookies if c['name'] == 'sessionID'), None)
                token = next((c['value'] for c in cookies if c['name'] == 'token'), None)
                player_id = next((c['value'] for c in cookies if c['name'] == 'playerID'), None)

                if sid and token:
                    print(f"✅ SESSIONE AGGANCIATA!")
                    print(f"🔑 ID: {sid[:8]}... | Token: {token[:8]}...")
                    
                    # Salviamo tutto per il Brain
                    with open("session_data.txt", "w") as f:
                        f.write(f"sessionID={sid}\ntoken={token}\nplayerID={player_id}")
                    
                    return RePanzaClient(sid)
                
                # Se non li trova, salviamo lo screenshot per capire se la pagina è diversa
                page.screenshot(path="debug_cookies_missing.png")
                print("❌ Cookie non trovati nel contesto del browser.")
                
            except Exception as e:
                print(f"💥 Errore: {e}")
            
            browser.close()
            return None
