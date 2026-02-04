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
                
                # Selettore specifico per evitare il conflitto con Italia VII
                # Usiamo .first per assicurarci di prendere il primo elemento trovato
                selector_mondo = page.locator(".button-game-world--title:has-text('Italia VI')").first
                selector_ok = page.locator("button:has-text('OK')")
                
                for i in range(120):
                    # 1. Gestione Manutenzione
                    if selector_ok.is_visible():
                        print("🛠️ Manutenzione rilevata. Premo OK...")
                        selector_ok.click()
                        time.sleep(2)
                    
                    # 2. Selezione Mondo (Risolve l'errore di duplicati)
                    if selector_mondo.is_visible():
                        print("🎯 Italia VI trovato. Entro...")
                        selector_mondo.click(force=True)
                        selector_mondo.evaluate("node => node.click()")
                    
                    # 3. Successo
                    if capture["sid"]:
                        sid_final = capture["sid"]
                        browser.close()
                        return RePanzaClient(sid_final)
                    
                    time.sleep(1)
                
                print("❌ Timeout finale.")
                page.screenshot(path="debug_final.png")
                
            except Exception as e:
                print(f"⚠️ Errore: {e}")
            
            browser.close()
            return None
