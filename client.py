from playwright.sync_api import sync_playwright
import time
import os
import requests
import json
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
            # User agent reale per evitare blocchi
            context = browser.new_context(viewport={'width': 1280, 'height': 720}, 
                                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            page = context.new_page()
            
            capture = {"sid": None}

            def intercept_response(response):
                # Cerchiamo ovunque nel pacchetto login
                if "login" in response.url and response.status == 200:
                    try:
                        # 1. Controllo COOKIE (Memoria)
                        cookies = context.cookies()
                        for c in cookies:
                            if c['name'] == 'sessionID':
                                capture["sid"] = c['value']
                                return

                        # 2. Controllo CORPO RISPOSTA (JSON)
                        try:
                            text = response.text()
                            if "sessionID" in text:
                                # Cerca "sessionID":"..." oppure "sessionID" : "..."
                                match = re.search(r'sessionID["\s:]+([a-z0-9\-]+)', text)
                                if match:
                                    capture["sid"] = match.group(1)
                        except:
                            pass
                    except:
                        pass

            page.on("response", intercept_response)
            
            try:
                print("🌐 Caricamento Lords & Knights...")
                page.goto("https://www.lordsandknights.com/", wait_until="networkidle", timeout=90000)
                
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                selector_mondo = ".button-game-world--title:has-text('Italia VI')"
                print("⏳ Attesa comparsa mondi...")
                page.wait_for_selector(selector_mondo, timeout=30000)
                
                print("🎯 Click su Italia VI...")
                # Triplo metodo di click per forzare l'ingresso
                btn = page.locator(selector_mondo).first
                btn.click(force=True)
                time.sleep(1)
                btn.evaluate("node => node.click()")
                
                print("📡 In ascolto per il sessionID...")
                # Attesa aumentata a 120s per i runner lenti di GitHub
                for i in range(120):
                    if capture["sid"]:
                        sid_final = capture["sid"]
                        print(f"✅ SID CATTURATO AL SECONDO {i}: {sid_final[:10]}...")
                        browser.close()
                        return RePanzaClient(sid_final)
                    
                    time.sleep(1)
                    if i % 10 == 0 and i > 0:
                        print(f"   ...attesa {i}s ...")
                
                print("❌ Timeout: SID non arrivato.")
                page.screenshot(path="debug_timeout.png")
                
            except Exception as e:
                print(f"⚠️ Errore nel processo: {e}")
            
            browser.close()
            return None
