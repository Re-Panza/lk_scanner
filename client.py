from playwright.sync_api import sync_playwright
import time
import os
import requests
import re

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id

    @staticmethod
    def send_telegram_alert(message):
        token = os.getenv("TELEGRAM_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if token and chat_id:
            try:
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                            data={"chat_id": chat_id, "text": message}, timeout=5)
            except:
                pass

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()
            
            capture = {"sid": None}

            # Sniffer di rete per intercettare il pacchetto login
            def intercept_response(response):
                if "login" in response.url and response.status == 200:
                    try:
                        # 1. Controllo dai Cookie
                        cookies = context.cookies()
                        for c in cookies:
                            if c['name'] == 'sessionID':
                                capture["sid"] = c['value']
                        
                        # 2. Controllo dal corpo JSON (Backup)
                        if not capture["sid"]:
                            text = response.text()
                            match = re.search(r'sessionID["\s:]+([a-z0-9\-]+)', text)
                            if match:
                                capture["sid"] = match.group(1)
                    except:
                        pass

            page.on("response", intercept_response)
            
            try:
                print("🌐 Caricamento Lords & Knights...")
                page.goto("https://www.lordsandknights.com/", wait_until="networkidle", timeout=90000)
                
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # Selezione Mondo
                selector_mondo = ".button-game-world--title:has-text('Italia VI')"
                print("⏳ Attesa comparsa mondi...")
                page.wait_for_selector(selector_mondo, timeout=40000)
                
                print("🎯 Click su Italia VI...")
                btn = page.locator(selector_mondo).first
                btn.click(force=True)
                btn.evaluate("node => node.click()") # Click JS di rinforzo
                
                print("📡 In ascolto per il sessionID...")
                # Attesa estesa a 120s per runner lenti
                for i in range(120):
                    if capture["sid"]:
                        sid_final = capture["sid"]
                        print(f"✅ SID CATTURATO: {sid_final[:10]}...")
                        browser.close()
                        return RePanzaClient(sid_final)
                    
                    if i % 10 == 0 and i > 0:
                        print(f"   ...attesa {i}s ...")
                    time.sleep(1)
                
                # SE FALLISCE: Screenshot per capire dove siamo bloccati
                print("❌ Timeout! Salvo screenshot di debug...")
                page.screenshot(path="debug_timeout_view.png")
                
            except Exception as e:
                print(f"⚠️ Errore nel processo: {e}")
                page.screenshot(path="debug_error_view.png")
            
            browser.close()
            return None
