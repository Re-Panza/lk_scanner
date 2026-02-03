import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        # Endpoint Mondo 327 derivato dal tuo log di scansione
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Effettua il mirroring del login browser usando l'hash catturato"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': 'f5c411a2d7b216ecf64213eb9b62fb77d27fe73fa398d94766c547d553cd05fd',
            'apiVersion': '1.0',
            'platform': 'browser'
        }
        
        # Header sincronizzati con il tuo curl per evitare 'Login rifiutato'
        headers = {
            'Accept': 'application/x-bplist',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
            'XYClient-Client': 'lk_b_3',
            'XYClient-Loginclient': 'Chrome',
            'XYClient-Loginclientversion': '10.8.0',
            'XYClient-Platform': 'browser'
        }

        try:
            print(f"📡 Tentativo Login Mirroring per {email}...")
            # Timeout esteso per evitare 'Read timed out'
            response = requests.post(login_url, data=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                if sid:
                    print("✅ LOGIN SUCCESSO!")
                    return RePanzaClient(sid)
                else:
                    print(f"❌ Login rifiutato: {data.get('localized', 'Credenziali o DeviceID non validi')}")
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
        except: return None
