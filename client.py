import requests
import plistlib
import hashlib
import time

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Login con mirroring browser e ID dispositivo rigenerato"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        # Generiamo un deviceId unico basato sulla tua email per costanza
        bot_device_id = hashlib.sha256(f"re-panza-{email}".encode()).hexdigest()
        
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'logoutUrl': 'http://lordsandknights.com/',
            'deviceId': bot_device_id
        }
        
        headers = {
            'Accept': 'application/x-bplist',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.lordsandknights.com',
            'Referer': 'https://www.lordsandknights.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'XYClient-Client': 'lk_b_3',
            'XYClient-Platform': 'browser',
            'XYClient-Loginclient': 'Chrome',
            'XYClient-Loginclientversion': '10.8.0'
        }

        try:
            print(f"📡 Tentativo Login Bot-ID: {email}...")
            response = requests.post(login_url, data=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                
                if sid:
                    print("✅ LOGIN SUCCESSO!")
                    return RePanzaClient(sid)
                else:
                    # Se fallisce qui con quell'hash lungo, il problema è l'hash stesso
                    print(f"❌ Rifiutato dal server: {data.get('localized', 'Credenziali non valide')}")
                    print(f"DEBUG: {data}")
            return None
        except Exception as e:
            print(f"💥 Errore: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Recupera la classifica Mondo 327"""
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        headers = {'Accept': 'application/x-bplist', 'User-Agent': 'lk_b_3'}
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                return plistlib.loads(response.content)
            return None
        except Exception:
            return None
