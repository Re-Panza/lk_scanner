import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        # URL specifico per il Game Server del Mondo 327
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Effettua il login usando l'endpoint Mobile (più affidabile del Browser)"""
        # CAMBIO FONDAMENTALE: Usiamo authenticateUser invece di checkValidLoginBrowser
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/authenticateUser"
        
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': 're-panza-brain-v1',
            'apiVersion': '1.0' # Parametro spesso richiesto dall'endpoint mobile
        }
        
        headers = {
            'Accept': 'application/x-bplist',
            'User-Agent': 'LordsAndKnights/9.4.2 (iPhone; iOS 16.0; Scale/3.00)',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            print(f"📡 Tentativo di login (Mobile Auth): {email}...")
            response = requests.post(login_url, data=payload, headers=headers, timeout=15)
            
            # Se la risposta è 200, proviamo a leggere il plist
            if response.status_code == 200:
                try:
                    data = plistlib.loads(response.content)
                except Exception:
                    print(f"❌ Errore decodifica risposta: {response.text[:100]}")
                    return None

                sid = data.get('sessionID')
                
                if sid:
                    print("✅ Login Successo! SessionID recuperato.")
                    return RePanzaClient(sid)
                else:
                    # Se non c'è sessionID, stampiamo l'errore esatto
                    print(f"❌ Login rifiutato: {data.get('faultString', 'Errore generico')}")
                    # Questo debug ci dirà se dobbiamo cambiare ancora qualcosa
                    print(f"DEBUG RESPONSE: {data}")
            else:
                print(f"❌ Errore Server {response.status_code}")
                
            return None
        except Exception as e:
            print(f"💥 Errore critico durante il login: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Recupera la classifica usando il sessionID"""
        params = {
            'sessionID': self.session_id,
            'offset': offset,
            'limit': limit
        }
        
        headers = {
            'Accept': 'application/x-bplist',
            'User-Agent': 'LordsAndKnights/9.4.2 (iPhone; iOS 16.0; Scale/3.00)'
        }
        
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                return plistlib.loads(response.content)
            else:
                print(f"❌ Errore recupero classifica: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Errore di rete durante il fetch: {e}")
            return None
