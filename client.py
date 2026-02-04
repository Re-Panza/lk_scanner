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
        
        # Inseriamo le capabilities esatte viste nel tuo browser
        capabilities = "base%2Cfortress%2Ccity%2Cparti%D0%B0l%CE%A4ran%D1%95its%2Cstarterpack%2CrequestInformation%2CpartialUpdate%2Cregions%2Cmetropolis"
        
        headers = {
            'Accept': 'application/x-bplist',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': user_agent,
            'XYClient-Capabilities': capabilities,
            'XYClient-Client': 'lk_b_3',
            'XYClient-Loginclient': 'Chrome',
            'XYClient-Loginclientversion': '10.8.0',
            'XYClient-Platform': 'browser',
            'XYClient-PlatformLanguage': 'it',
            'Origin': 'https://www.lordsandknights.com',
            'Referer': 'https://www.lordsandknights.com/'
        }

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
            # Chiamata obbligatoria per inizializzare i cookie di sessione
            login_res = session.post("https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser", data=payload, headers=headers)
            
            print("📡 Step 2: Richiesta Token su Backend3...")
            payload['worldId'] = '327'
            token_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/LoginAction/token"
            
            # Inviamo la richiesta al Backend3 includendo i cookie ottenuti dallo Step 1
            response = session.post(token_url, data=payload, headers=headers)
            
            try:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                if sid:
                    print(f"✅ LOGIN COMPLETATO! Sessione Mondo 327 agganciata.")
                    world_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction"
                    return RePanzaClient(sid, world_url)
                else:
                    print(f"❌ Errore dal server: {data.get('localized', 'Credenziali o DeviceID non sincronizzati')}")
            except:
                # Se fallisce qui, stampiamo i primi 100 caratteri della risposta per capire l'errore
                print(f"💥 Errore: Risposta non PLIST. Anteprima: {response.text[:100]}")
                
            return None
        except Exception as e:
            print(f"💥 Errore tecnico durante il login: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        headers = {'Accept': 'application/x-bplist', 'User-Agent': 'lk_b_3'}
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=20)
            return plistlib.loads(response.content) if response.status_code == 200 else None
        except:
            return None
