import requests
import plistlib
import os

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        # Server specifico per il Mondo 327
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        # Recupero del DeviceID aggiornato dai Secrets
        device_id = os.getenv('LK_DEVICE_ID')
        
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': device_id,
            'apiVersion': '1.0',
            'platform': 'browser'
        }
        
        # Mirroring degli Header estratti da Chrome 144
        headers = {
            'Accept': 'application/x-bplist',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'XYClient-Client': 'lk_b_3',
            'XYClient-Loginclient': 'Chrome',
            'XYClient-Loginclientversion': '10.8.0',
            'XYClient-Platform': 'browser',
            'XYClient-PlatformLanguage': 'it'
        }

        try:
            print(f"📡 Tentativo Login Mirroring per {email}...")
            response = requests.post(login_url, data=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                if sid:
                    print(f"✅ LOGIN SUCCESSO! Sessione: {sid[:8]}...")
                    return RePanzaClient(sid)
                else:
                    # Stampa l'errore specifico restituito dal server
                    print(f"❌ Login rifiutato dal server: {data.get('localized', 'Errore sconosciuto')}")
            return None
        except Exception as e:
            print(f"💥 Errore tecnico: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        headers = {'Accept': 'application/x-bplist', 'User-Agent': 'lk_b_3'}
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=20)
            return plistlib.loads(response.content) if response.status_code == 200 else None
        except:
            return None
