from playwright.sync_api import sync_playwright
import time
import os
import requests

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()
            capture = {"sid": None}

            def intercept_response(response):
                if "login" in response.url and response.status == 200:
                    try:
                        cookies = context.cookies()
                        for c in cookies:
                            if c['name'] == 'sessionID':
                                capture["sid"] = c['value']
                                print(f"✅ SID INTERCETTATO: {capture['sid'][:10]}...")
                    except: pass

            page.on("response", intercept_response)
            
            try:
                print("🌐 Caricamento Lords & Knights...")
                page.goto("https://www.lordsandknights.com/", wait_until="networkidle", timeout=90000)
                
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                page.click('button:has-text("LOG IN")')
                
                # Attesa mondi o manutenzione
                selector_mondo = ".button-game-world--title:has-text('Italia VI')"
                selector_ok = "button:has-text('OK')"
                
                for i in range(120):
                    # 1. Se compare il tasto OK (Manutenzione), lo premiamo
                    if page.locator(selector_ok).is_visible():
                        print("🛠️ Rilevata manutenzione! Premo OK per forzare...")
                        page.locator(selector_ok).click()
                        time.sleep(2)
                    
                    # 2. Se compare il mondo, lo clicchiamo
                    if page.locator(selector_mondo).is_visible():
                        print("🎯 Mondo trovato! Click su Italia VI...")
                        page.locator(selector_mondo).first.click(force=True)
                        page.locator(selector_mondo).first.evaluate("node => node.click()")
                    
                    # 3. Se abbiamo il SID, usciamo con successo
                    if capture["sid"]:
                        sid_final = capture["sid"]
                        browser.close()
                        return RePanzaClient(sid_final)
                    
                    if i % 10 == 0: print(f"📡 In attesa... ({i}s)")
                    time.sleep(1)
                
                print("❌ Timeout finale raggiunto.")
                page.screenshot(path="debug_final_attempt.png")
                
            except Exception as e:
                print(f"⚠️ Errore: {e}")
            
            browser.close()
            return None
