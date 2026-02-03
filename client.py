import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        # URL per il Game Server del Mondo 327
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Login che emula esattamente la richiesta catturata dal browser"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        # Dati estratti dalla tua --data-raw
        # Nota: worldId nel tuo curl era 'null', ma noi forziamo '327' per entrare nel mondo giusto
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'logoutUrl': 'http://lordsandknights.com/',
            'deviceId': 'f5c411a2d7b216ecf64213eb9b62fb77d27fe73fa398d94766c547d553cd05fd'
        }
        
        # Header estratti esattamente dal tuo comando curl
        headers = {
            'Accept': 'application/x-bplist',
            'Accept-Language': 'it',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.lordsandknights.com',
            'Referer': 'https://www.lordsandknights.com/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
            'XYClient-Capabilities': 'base,fortress,city,partialTransits,starterpack,requestInformation,partialUpdate,regions,metropolis',
            'XYClient-Client': 'lk_b_3',
            'XYClient-Loginclient': 'Chrome',
            'XYClient-Loginclientversion': '10.8.0',
            'XYClient-Platform': 'browser',
            'XYClient-PlatformLanguage': 'it'
        }

        try:
            print(f"📡 Tentativo Login Mirroring: {email}...")
            # Invio della richiesta POST con i parametri esatti
            response = requests.post(login_url, data=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                
                if sid:
                    print("✅ LOGIN SUCCESSO! Sessione clonata correttamente.")
                    return RePanzaClient(sid)
                else:
                    print(f"❌ Login rifiutato: {data.get('localized', 'Credenziali o DeviceID non validi')}")
                    print(f"DEBUG: {data}")
            else:
                print(f"❌ Errore Server {response.status_code}")
            return None
        except Exception as e:
            print(f"💥 Errore critico: {e}")
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
