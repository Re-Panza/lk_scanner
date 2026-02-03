import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Mirroring perfetto basato sui dati Charles Proxy"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            # Usa il deviceId del browser o quello visto nel software se diverso
            'deviceId': '0cfb112df2c7e5eb34ad351eb4123f4b398ad9447ddfe36e41ce1f85f26a27ca',
            'apiVersion': '1.0',
            'platform': 'browser'
        }
        
        # Header estratti da Charles Proxy
        headers = {
            'Accept': 'application/x-bplist',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36',
            'XYClient-Client': 'lk_b_3',
            'XYClient-Loginclient': 'Chrome',
            'XYClient-Loginclientversion': '8.7.0',
            'XYClient-Platform': 'browser',
            'XYClient-PlatformLanguage': 'en'
        }

        try:
            print(f"📡 Tentativo Login Mirroring per {email}...")
            response = requests.post(login_url, data=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                if sid:
                    print("✅ LOGIN SUCCESSO!")
                    return RePanzaClient(sid)
                else:
                    print(f"❌ Login rifiutato: {data.get('localized', 'Verifica Hash e DeviceID')}")
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
        except Exception:
            return None
