import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Effettua il login inviando i dati nel formato nativo bplist"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        # Prepariamo il payload per il server di login
        payload_dict = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': 're-panza-brain-v1'
        }
        
        # Trasformiamo il dizionario nel formato binario bplist
        try:
            payload_plist = plistlib.dumps(payload_dict)
        except Exception as e:
            print(f"❌ Errore nella creazione del plist: {e}")
            return None
        
        headers = {
            'Content-Type': 'application/x-bplist',
            'Accept': 'application/x-bplist',
            'User-Agent': 'LordsAndKnights/9.4.2 (iPhone; iOS 16.0; Scale/3.00)'
        }

        try:
            print(f"📡 Tentativo di login: {email}...")
            response = requests.post(login_url, data=payload_plist, headers=headers, timeout=15)
            
            print(f"DEBUG: HTTP Status {response.status_code}")
            
            if response.status_code == 200:
                # Decodifichiamo la risposta bplist
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                
                if sid:
                    print("✅ Login Successo! SessionID generato.")
                    return RePanzaClient(sid)
                else:
                    # Se il login fallisce, stampiamo il motivo restituito dal server
                    print(f"❌ Login fallito dal server: {data.get('faultString', 'Motivo sconosciuto')}")
                    print(f"DEBUG RESPONSE: {data}")
            else:
                print(f"❌ Errore Server {response.status_code}: {response.text}")
                
            return None
        except Exception as e:
            print(f"💥 Errore critico di connessione: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Recupera la classifica usando il sessionID"""
        params = {
            'sessionID': self.session_id,
            'offset': offset,
            'limit': limit
        }
        
        headers = {'Accept': 'application/x-bplist'}
        
        try:
            # Nota: qui usiamo GET come da standard delle API di gioco per i ranking
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                return plistlib.loads(response.content)
            return None
        except Exception as e:
            print(f"❌ Errore nel recupero classifica: {e}")
            return None
