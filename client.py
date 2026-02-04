import requests
import plistlib

class RePanzaClient:
    def __init__(self, session_id, player_id, login_id):
        self.session_id = session_id
        self.player_id = player_id
        self.login_id = login_id
        # Endpoint Backend3 dal tuo curl
        self.base_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction"

    @staticmethod
    def from_existing_session(sid, pid, lid):
        print(f"🚀 Utilizzo sessione esistente: {sid[:8]}...")
        return RePanzaClient(sid, pid, lid)

    def fetch_rankings(self, offset=0, limit=50):
        # Costruiamo i cookie esattamente come nel tuo curl 'update'
        cookies = {
            'sessionID': self.session_id,
            'playerID': self.player_id,
            'loginID': self.login_id,
            'logoutUrl': 'http://lordsandknights.com/'
        }
        
        params = {
            'sessionID': self.session_id,
            'offset': offset,
            'limit': limit,
            'worldID': '327'
        }
        
        headers = {
            'Accept': 'application/x-bplist',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
            'XYClient-Client': 'lk_b_3'
        }

        try:
            response = requests.get(f"{self.base_url}/rankings", params=params, cookies=cookies, headers=headers, timeout=20)
            if response.status_code == 200:
                return plistlib.loads(response.content)
            print(f"❌ Errore Ranking: Status {response.status_code}")
            return None
        except Exception as e:
            print(f"💥 Errore richiesta: {e}")
            return None
