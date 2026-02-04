import requests
import plistlib
import os

class RePanzaClient:
    def __init__(self, session_id, base_url):
        self.session_id = session_id
        self.base_url = base_url

    @staticmethod
    def auto_login(email, password_hash):
        device_id = os.getenv('LK_DEVICE_ID')
        # User Agent specifico dal tuo curl (Nexus 5 Emulator)
        user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36"
        
        headers = {
            'Accept': 'application/x-bplist',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': user_agent,
            'XYClient-Client': 'lk_b_3',
            'XYClient-Loginclient': 'Chrome',
            'XYClient-Loginclientversion': '10.8.0',
            'XYClient-Platform': 'browser',
            'XYClient-PlatformLanguage': 'it'
        }

        # STEP 1: Check Valid Login
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': 'null',
            'deviceId': device_id,
            'apiVersion': '1.0',
            'platform': 'browser'
        }

        session = requests.Session() # Usiamo una sessione per gestire i cookie (playerID, loginID)
        try:
            print(f"📡 Step 1: Validazione iniziale per {email}...")
            res1 = session.post(login_url, data=payload, headers=headers)
            
            # STEP 2: Ottenere il Token dal Backend 3 (come visto nel tuo curl)
            token_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/LoginAction/token"
            payload['worldId'] = '327'
            
            print("📡 Step 2: Recupero Token dal Backend3...")
            res2 = session.post(token_url, data=payload, headers=headers)
            data = plistlib.loads(res2.content)
            
            sid = data.get('sessionID')
            if sid:
                print(f"✅ LOGIN COMPLETATO! Sessione Mondo 327 attiva.")
                # Endpoint per i ranking su Backend 3
                world_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction"
                return RePanzaClient(sid, world_url)
            
            print(f"❌ Fallito: {data.get('localized', 'Errore sequenza login')}")
            return None
        except Exception as e:
            print(f"💥 Errore: {e}")
            return None
