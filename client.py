import requests
import plistlib
import os

class RePanzaClient:
    def __init__(self, session_id, base_url):
        self.session_id = session_id
        self.base_url = base_url

    @staticmethod
    def auto_login(email, password_hash):
        # Utilizziamo il DeviceID estratto dal tuo curl browser
        device_id = os.getenv('LK_DEVICE_ID', 'b3d3d6a165b29d1310097d30c81783abefdeee1b140025b9e3abff2077605e58')
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

        session = requests.Session()
        # Payload standard basato sulla tua sessione attiva
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'logoutUrl': 'http://lordsandknights.com/',
            'deviceId': device_id
        }

        try:
            print(f"📡 Step 1: Validazione iniziale per {email}...")
            # Chiamata al Login Server centrale
            session.post("https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser", data=payload, headers=headers)
            
            print("📡 Step 2: Recupero Token dal Backend3...")
            # Endpoint specifico per il Mondo 327 su Backend 3
            token_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/LoginAction/token"
            response = session.post(token_url, data=payload, headers=headers)
            
            try:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                if sid:
                    print(f"✅ LOGIN COMPLETATO! Sessione Mondo 327 attiva.")
                    world_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction"
                    return RePanzaClient(sid, world_url)
                else:
                    print(f"❌ Fallito: {data.get('localized', 'Dati sessione non trovati')}")
            except Exception:
                print(f"💥 Errore: Risposta server non valida (Formato non PLIST).")
            return None
        except Exception as e:
            print(f"💥 Errore tecnico: {e}")
            return None
