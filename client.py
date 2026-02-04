from playwright.sync_api import sync_playwright
import time

class RePanzaClient:
    def __init__(self, session_id, token):
        self.session_id = session_id
        self.token = token

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            print(f"🌐 Caricamento Lords & Knights...")
            page.goto("https://www.lordsandknights.com/", wait_until="networkidle")
            
            try:
                # 1. Inserimento credenziali
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                
                # Clicchiamo e aspettiamo che il traffico di login si calmi
                page.click('button:has-text("LOG IN")')
                print("⏳ Attesa validazione credenziali...")
                time.sleep(10)
                
                # 2. Selezione Mondo e Attesa Risposta
                print("🎯 Selezione Italia VI...")
                # Usiamo le coordinate confermate per il click balistico
                page.mouse.click(300, 230) 
                
                # Aspettiamo che il file 'login' passi e depositi i cookie
                print("🏰 Entrata nel mondo... Estrazione cookie di sessione...")
                time.sleep(15) 

                # 3. Estrazione massiva dal contesto
                cookies = context.cookies()
                sid = next((c['value'] for c in cookies if c['name'] == 'sessionID'), None)
                token = next((c['value'] for c in cookies if c['name'] == 'token'), None)

                if sid:
                    print(f"✅ SESSIONE AGGANCIATA!")
                    print(f"🔑 SID: {sid[:8]}... | Token: {token[:8] if token else 'N/D'}...")
                    
                    with open("session_data.txt", "w") as f:
                        f.write(f"SID={sid}\nTOKEN={token}")
                    return RePanzaClient(sid, token)
                
                # Se fallisce, salviamo i cookie trovati per debug
                print(f"❌ SID non trovato. Cookie rilevati: {[c['name'] for c in cookies]}")
                page.screenshot(path="debug_final_check.png")
                
            except Exception as e:
                print(f"💥 Errore critico: {e}")
            
            browser.close()
            return None
