import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        # URL per il Game Server del Mondo 327
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Login ibrido: usa MD5 permanente con identità browser del tuo curl"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        # Usiamo il deviceId e i parametri catturati dal tuo browser
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
            print(f"📡 Tentativo Login Finale (MD5 Mode): {email}...")
            # Aumentiamo il timeout a 25 per evitare l'errore visto nell'ultima immagine
            response = requests.post(login_url, data=payload, headers=headers, timeout=25)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                
                if sid:
                    print("✅ LOGIN SUCCESSO! Scanner avviato.")
                    return RePanzaClient(sid)
                else:
                    print(f"❌ Server rifiuta credenziali: {data.get('localized', 'Hash errato')}")
            else:
                print(f"❌ Errore HTTP {response.status_code}")
            return None
        except Exception as e:
            print(f"💥 Errore connessione: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Recupera i dati della classifica"""
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        headers = {'Accept': 'application/x-bplist', 'User-Agent': 'lk_b_3'}
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=20)
            if response.status_code == 200:
                return plistlib.loads(response.content)
            return None
        except Exception:
            return None
