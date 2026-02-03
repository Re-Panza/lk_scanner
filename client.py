import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Login tramite endpoint Browser con fix per parametri mancanti"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        # Parametri minimi ma completi per l'endpoint Browser
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': 're-panza-brain-v1',
            'timezone': 'Europe/Rome' # Parametro spesso obbligatorio per evitare 'Insufficient parameters'
        }
        
        headers = {
            'Accept': 'application/x-bplist',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            print(f"📡 Tentativo Login Browser-Mode: {email}...")
            # Invio esplicito dei dati per garantire la formattazione corretta
            response = requests.post(login_url, data=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                
                if sid:
                    print("✅ Login Successo!")
                    return RePanzaClient(sid)
                else:
                    # Debug dettagliato dell'errore dal server
                    print(f"❌ Login rifiutato: {data.get('localized', 'Dati insufficienti o errati')}")
                    print(f"DEBUG RESPONSE: {data}")
            else:
                print(f"❌ Errore Server {response.status_code}")
                
            return None
        except Exception as e:
            print(f"💥 Errore critico: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Recupera la classifica"""
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        headers = {'Accept': 'application/x-bplist'}
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                return plistlib.loads(response.content)
            return None
        except Exception:
            return None
