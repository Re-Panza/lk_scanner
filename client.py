import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        # URL per il Game Server del Mondo 327
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Login tramite endpoint standard per massimizzare la compatibilità"""
        # Utilizziamo l'endpoint di login più semplice disponibile
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/login"
        
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': 're-panza-brain-v1',
            'apiVersion': '1.0'
        }
        
        headers = {
            'Accept': 'application/x-bplist',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'LordsAndKnights/9.4.2 (iPhone; iOS 16.0; Scale/3.00)'
        }

        try:
            print(f"📡 Tentativo Login (Legacy Mode): {email}...")
            # Invio dati come form-data standard
            response = requests.post(login_url, data=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = plistlib.loads(response.content)
                except Exception:
                    print(f"❌ Errore decodifica: {response.text[:100]}")
                    return None

                sid = data.get('sessionID')
                
                if sid:
                    print("✅ Login Successo! SessionID ottenuto.")
                    return RePanzaClient(sid)
                else:
                    # Log del motivo del rifiuto
                    error_msg = data.get('localized', data.get('faultString', 'Credenziali o parametri errati'))
                    print(f"❌ Login rifiutato: {error_msg}")
                    print(f"DEBUG: {data}")
            else:
                print(f"❌ Server Error {response.status_code}")
                
            return None
        except Exception as e:
            print(f"💥 Errore critico: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Recupera la classifica giocatori"""
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        headers = {'Accept': 'application/x-bplist'}
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                return plistlib.loads(response.content)
            return None
        except Exception:
            return None
