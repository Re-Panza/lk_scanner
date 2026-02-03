import requests
import plistlib
import hashlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Login che clona l'identità del tuo browser per accettare l'MD5"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        # Usiamo il deviceId del tuo curl per massima coerenza
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': 'f5c411a2d7b216ecf64213eb9b62fb77d27fe73fa398d94766c547d553cd05fd',
            'apiVersion': '1.0',
            'platform': 'browser'
        }
        
        headers = {
            'Accept': 'application/x-bplist',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
            'XYClient-Client': 'lk_b_3',
            'XYClient-Loginclient': 'Chrome',
            'XYClient-Loginclientversion': '10.8.0',
            'XYClient-Capabilities': 'base,fortress,city,partialTransits,starterpack,requestInformation,partialUpdate,regions,metropolis'
        }

        try:
            print(f"📡 Tentativo Login (Identity Clone): {email}...")
            response = requests.post(login_url, data=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                
                if sid:
                    print("✅ LOGIN SUCCESSO!")
                    return RePanzaClient(sid)
                else:
                    print(f"❌ Rifiutato dal server: {data.get('localized', 'Credenziali non valide')}")
            return None
        except Exception as e:
            print(f"💥 Errore tecnico: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Recupera la classifica"""
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        headers = {'Accept': 'application/x-bplist', 'User-Agent': 'lk_b_3'}
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                return plistlib.loads(response.content)
            return None
        except Exception:
            return None
