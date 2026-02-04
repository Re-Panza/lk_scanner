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
        user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36"
        
        headers = {
            'Accept': 'application/x-bplist',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': user_agent,
            'XYClient-Client': 'lk_b_3',
            'XYClient-Loginclient': 'Chrome',
            'XYClient-Loginclientversion': '10.8.0',
            'XYClient-Platform': 'browser',
            'XYClient-PlatformLanguage': 'it',
            'Origin': 'https://www.lordsandknights.com',
            'Referer': 'https://www.lordsandknights.com/'
        }

        # Usiamo requests.Session() per mantenere i cookie tra le chiamate
        session = requests.Session()
        
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': 'null',
            'logoutUrl': 'http://lordsandknights.com/',
            'deviceId': device_id
        }

        try:
            print(f"📡 Step 1: Validazione su LoginServer...")
            # Questa chiamata imposta i cookie iniziali nel 'session' object
            session.post("https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser", data=payload, headers=headers)
            
            print("📡 Step 2: Richiesta Token su Backend3...")
            # Cambiamo worldId per la chiamata al server di gioco
            payload['worldId'] = '327'
            token_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/LoginAction/token"
            
            response = session.post(token_url, data=payload, headers=headers)
            
            # Se il server risponde con errore, proviamo a leggere il contenuto
            try:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                if sid:
                    print(f"✅ LOGIN OK! Sessione attiva.")
                    world_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction"
                    return RePanzaClient(sid, world_url)
                else:
                    print(f"❌ Server dice: {data.get('localized', 'Credenziali non valide')}")
            except:
                print(f"💥 Errore: Risposta non PLIST (Probabile errore 404 o 500 del backend)")
                
            return None
        except Exception as e:
            print(f"💥 Errore tecnico: {e}")
            return None
