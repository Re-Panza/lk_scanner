import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        # Endpoint validato per il Mondo 327
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Mirroring perfetto della sessione browser catturata per il login"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            # Usiamo il deviceId estratto dal tuo ultimo curl
            'deviceId': '0cfb112df2c7e5eb34ad351eb4123f4b398ad9447ddfe36e41ce1f85f26a27ca',
            'apiVersion': '1.0',
            'platform': 'browser'
        }
        
        # Header sincronizzati con il tuo ambiente browser
        headers = {
            'Accept': 'application/x-bplist',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
            'XYClient-Client': 'lk_b_3',
            'XYClient-Loginclient': 'Chrome',
            'XYClient-Loginclientversion': '10.8.0',
            'XYClient-Platform': 'browser',
            'XYClient-PlatformLanguage': 'it'
        }

        try:
            print(f"📡 Mirroring Login in corso per {email}...")
            # Timeout a 30s per garantire stabilità durante la scansione
            response = requests.post(login_url, data=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                if sid:
                    print("✅ LOGIN SUCCESSO! Sessione agganciata.")
                    return RePanzaClient(sid)
                else:
                    print(f"❌ Server rifiuta: {data.get('localized', 'Verifica credenziali e deviceId')}")
            return None
        except Exception as e:
            print(f"💥 Errore tecnico durante il login: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Recupera la classifica mondiale utilizzando il sessionID ottenuto"""
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        headers = {'Accept': 'application/x-bplist', 'User-Agent': 'lk_b_3'}
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=20)
            return plistlib.loads(response.content) if response.status_code == 200 else None
        except Exception:
            return None
