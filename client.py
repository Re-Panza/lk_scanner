import requests
import plistlib
import os

class RePanzaClient:
    def __init__(self, session_id, base_url):
        self.session_id = session_id
        self.base_url = base_url

    @staticmethod
    def auto_login(email, password_hash):
        # Questi dati ora vivono su GitHub, non sul tuo PC
        device_id = os.getenv('LK_DEVICE_ID')
        
        headers = {
            'Accept': 'application/x-bplist',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
            'XYClient-Capabilities': 'base%2Cfortress%2Ccity%2Cparti%D0%B0l%CE%A4ran%D1%95its%2Cstarterpack%2CrequestInformation%2CpartialUpdate%2Cregions%2Cmetropolis',
            'XYClient-Client': 'lk_b_3',
            'XYClient-Loginclient': 'Chrome',
            'XYClient-Loginclientversion': '10.8.0',
            'XYClient-Platform': 'browser',
            'XYClient-PlatformLanguage': 'it'
        }

        session = requests.Session()
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': device_id,
            'apiVersion': '1.0',
            'platform': 'browser'
        }

        try:
            # Step 1: Validazione
            session.post("https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser", data=payload, headers=headers)
            
            # Step 2: Token
            token_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/LoginAction/token"
            res = session.post(token_url, data=payload, headers=headers)
            
            data = plistlib.loads(res.content)
            sid = data.get('sessionID')
            
            if sid:
                print(f"✅ Login automatico riuscito! Sessione: {sid[:8]}")
                world_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction"
                return RePanzaClient(sid, world_url)
            
            print(f"❌ Errore login: {data.get('localized', 'Credenziali errate')}")
            return None
        except Exception as e:
            print(f"💥 Errore tecnico: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        try:
            res = requests.get(f"{self.base_url}/rankings", params=params, timeout=20)
            return plistlib.loads(res.content) if res.status_code == 200 else None
        except: return None
