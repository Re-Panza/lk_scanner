import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        # URL per il Game Server del Mondo 327
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Effettua il login inviando i dati in formato XML Plist per evitare 'Insufficient parameters'"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        # Struttura dati richiesta dal server
        payload_dict = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': 're-panza-brain-v1'
        }
        
        # Trasformiamo il dizionario in un XML Plist binario
        payload_xml = plistlib.dumps(payload_dict)
        
        headers = {
            'Accept': 'application/x-bplist',
            'Content-Type': 'application/x-apple-plist', # Indica al server che stiamo inviando un Plist
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        try:
            print(f"📡 Tentativo Login (XML Mode): {email}...")
            # Inviamo il Plist nel corpo della POST
            response = requests.post(login_url, data=payload_xml, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                
                if sid:
                    print("✅ Login Successo! SessionID ottenuto.")
                    return RePanzaClient(sid)
                else:
                    print(f"❌ Login rifiutato: {data.get('localized', 'Errore parametri o credenziali')}")
                    print(f"DEBUG RESPONSE: {data}")
            else:
                print(f"❌ Errore Server {response.status_code}")
                
            return None
        except Exception as e:
            print(f"💥 Errore critico: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Recupera la classifica usando il formato bplist per la risposta"""
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        headers = {'Accept': 'application/x-bplist'}
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                return plistlib.loads(response.content)
            return None
        except Exception:
            return None
