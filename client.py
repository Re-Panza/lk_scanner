import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        # URL specifico per il Game Server del Mondo 327
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def auto_login(email, password_hash):
        """Effettua il login simulando un device reale completo"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/authenticateUser"
        
        # FIX: Aggiunti TUTTI i parametri che un vero iPhone invia
        # Senza 'deviceType' o 'bundleId', il server rifiuta la connessione
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': 're-panza-brain-v1',
            'UDID': 're-panza-brain-v1',
            'platform': 'iPhone',
            'clientVersion': '9.4.2',
            'apiVersion': '1.0',
            # --- NUOVI PARAMETRI AGGIUNTI ---
            'deviceType': 'iPhone14,2',          # Modello specifico (iPhone 13 Pro)
            'osVersion': '16.0',                 # Versione iOS
            'bundleId': 'com.xyrality.lordsandknights', # Identificativo app
            'locale': 'it_IT',                   # Lingua e regione
            'language': 'it'                     # Lingua
        }
        
        headers = {
            'Accept': 'application/x-bplist',
            'User-Agent': 'LordsAndKnights/9.4.2 (iPhone; iOS 16.0; Scale/3.00)',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            print(f"📡 Login Mobile Full-Data: {email}...")
            response = requests.post(login_url, data=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = plistlib.loads(response.content)
                except Exception:
                    print(f"❌ Errore decodifica: {response.text[:100]}")
                    return None

                sid = data.get('sessionID')
                
                if sid:
                    print("✅ Login Successo! SessionID generato.")
                    return RePanzaClient(sid)
                else:
                    # Se fallisce ancora, stampiamo il debug completo
                    print(f"❌ Login rifiutato: {data.get('faultString', 'Errore')}")
                    print(f"DEBUG: {data}")
            else:
                print(f"❌ Server Error {response.status_code}")
                
            return None
        except Exception as e:
            print(f"💥 Errore critico: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Recupera la classifica"""
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
                print(f"❌ Errore classifica: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Errore fetch: {e}")
            return None
