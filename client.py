import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        # URL specifico per il Game Server del Mondo 327
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Effettua il login usando il formato form-data (standard per il login server)"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        # Inviamo i dati come un normale form (chiave=valore)
        # Questo risolve l'errore "Insufficient parameters" visto nei log
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': 're-panza-brain-v1'
        }
        
        headers = {
            'Accept': 'application/x-bplist',
            'User-Agent': 'LordsAndKnights/9.4.2 (iPhone; iOS 16.0; Scale/3.00)'
        }

        try:
            print(f"📡 Tentativo di login (form-mode): {email}...")
            # Usiamo data=payload per inviare i parametri nel corpo della POST come form-data
            response = requests.post(login_url, data=payload, headers=headers, timeout=15)
            
            print(f"DEBUG: HTTP Status {response.status_code}")
            
            if response.status_code == 200:
                # Anche se inviamo form-data, il server risponde in bplist
                try:
                    data = plistlib.loads(response.content)
                except Exception:
                    # Fallback nel caso la risposta non sia un plist valido
                    print("❌ Errore nella decodifica della risposta del server.")
                    return None

                sid = data.get('sessionID')
                
                if sid:
                    print("✅ Login Successo! SessionID recuperato.")
                    return RePanzaClient(sid)
                else:
                    # Mostra l'errore specifico restituito da Xyrality
                    print(f"❌ Login rifiutato: {data.get('faultString', 'Credenziali errate')}")
                    print(f"DEBUG RESPONSE: {data}")
            else:
                print(f"❌ Errore Server {response.status_code}: {response.text}")
                
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
            # Richiesta GET per ottenere i dati della classifica
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                return plistlib.loads(response.content)
            else:
                print(f"❌ Errore recupero classifica: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Errore di rete durante il fetch: {e}")
            return None
