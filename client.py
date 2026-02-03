import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Login ultra-compatibile con emulazione Browser/Mobile mista"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        # Parametri che hanno mostrato di generare risposte coerenti nei log
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': 're-panza-brain-v1',
            'platform': 'browser',
            'clientVersion': '9.4.2',
            'apiVersion': '1.0'
        }
        
        headers = {
            'Accept': 'application/x-bplist',
            'User-Agent': 'LordsAndKnights/9.4.2 (iPhone; iOS 16.0; Scale/3.00)',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            print(f"📡 Tentativo Login Finale: {email}...")
            response = requests.post(login_url, data=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                
                if sid:
                    print("✅ LOGIN SUCCESSO! SessionID ottenuto.")
                    return RePanzaClient(sid)
                else:
                    # Se il server risponde ma non dà il SID
                    msg = data.get('localized', data.get('faultString', 'Credenziali errate o account non esistente'))
                    print(f"❌ Server dice: {msg}")
                    print(f"DEBUG: {data}")
            else:
                print(f"❌ Errore di connessione al server: {response.status_code}")
            return None
        except Exception as e:
            print(f"💥 Errore durante l'invio: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Recupera la classifica"""
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        headers = {'Accept': 'application/x-bplist', 'User-Agent': 'LordsAndKnights/9.4.2'}
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                return plistlib.loads(response.content)
            return None
        except Exception:
            return None
