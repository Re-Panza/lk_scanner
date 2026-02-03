import requests
import plistlib
import hashlib

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        self.base_url = "https://lx-game.lordsandknights.com/XYRALITY/WebObjects/BKGameServer-327.woa/wa/PlayerAction"

    @staticmethod
    def generate_lk_sha256(password):
        """
        Replica esattamente il calcolo SHA-256 che fa il browser di L&K.
        Nota: Alcune versioni del sito aggiungono un salt specifico.
        """
        # Se il server accetta lo SHA-256 puro della stringa:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def auto_login(email, password_raw_or_hash):
        """
        Tenta il login. Se passi la password in chiaro, calcola lo SHA-256.
        """
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        
        # Se la stringa è corta (es. MD5 o pass chiara), proviamo a gestirla
        # Se è già di 64 caratteri, la usiamo così com'è.
        if len(password_raw_or_hash) != 64:
            pw_to_send = RePanzaClient.generate_lk_sha256(password_raw_or_hash)
        else:
            pw_to_send = password_raw_or_hash

        payload = {
            'login': email,
            'password': pw_to_send,
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
            'XYClient-Loginclientversion': '10.8.0'
        }

        try:
            print(f"📡 Tentativo Login SHA-256 Engine: {email}...")
            response = requests.post(login_url, data=payload, headers=headers, timeout=25)
            
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                if sid:
                    print("✅ LOGIN SUCCESSO!")
                    return RePanzaClient(sid)
                else:
                    print(f"❌ Errore: {data.get('localized', 'Credenziali non valide')}")
            return None
        except Exception as e:
            print(f"💥 Errore: {e}")
            return None

    def fetch_rankings(self, offset=0, limit=50):
        params = {'sessionID': self.session_id, 'offset': offset, 'limit': limit}
        headers = {'Accept': 'application/x-bplist', 'User-Agent': 'lk_b_3'}
        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, headers=headers, timeout=20)
            return plistlib.loads(response.content) if response.status_code == 200 else None
        except: return None
