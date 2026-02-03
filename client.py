import requests
import plistlib
import hashlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def get_nonce():
        """Recupera il codice nonce temporaneo dal server"""
        url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/nonce"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                return data.get('nonce')
        except Exception:
            return None
        return None

    @staticmethod
    def auto_login(email, password_hash):
        """Effettua il login utilizzando il sistema di sicurezza Nonce"""
        nonce = RePanzaClient.get_nonce()
        if not nonce:
            print("❌ Impossibile recuperare il Nonce dal server.")
            return None

        # La password finale deve essere MD5(password_hash + nonce)
        final_hash = hashlib.md5((password_hash + nonce).encode()).hexdigest()
        
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/authenticateUser"
        
        payload = {
            'login': email,
            'password': final_hash,
            'nonce': nonce,
            'worldId': '327',
            'deviceId': 're-panza-brain-v1',
            'platform': 'iPhone',
            'clientVersion': '9.4.2',
            'apiVersion': '1.0'
        }
        
        headers = {
            'Accept': 'application/x-bplist',
            'User-Agent': 'LordsAndKnights/9.4.2 (iPhone; iOS 16.0; Scale/3.00)',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            print(f"📡 Login con Nonce Security: {email}...")
            response = requests.post(login_url, data=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                
                if sid:
                    print("✅ Login Successo! SessionID creato.")
                    return RePanzaClient(sid)
                else:
                    print(f"❌ Login rifiutato: {data.get('faultString', 'Parametri insufficienti')}")
                    print(f"DEBUG: {data}")
            else:
                print(f"❌ Errore Server {response.status_code}")
                
            return None
        except Exception as e:
            print(f"💥 Errore critico: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Scarica la classifica utilizzando la sessione attiva"""
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        headers = {'Accept': 'application/x-bplist', 'User-Agent': 'LordsAndKnights/9.4.2'}
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                return plistlib.loads(response.content)
            return None
        except Exception:
            return None
