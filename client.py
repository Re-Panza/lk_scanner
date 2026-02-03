import requests
import plistlib
import time

class RePanzaClient:
    def __init__(self, session_id):
        self.session_id = session_id
        # Backend 3 per Mondo 327
        self.base_url = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-IT-15.woa/wa/QueryAction"
        self.headers = {
            'Accept': 'application/x-bplist',
            'XYClient-Client': 'lk_b_3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.cookies = {'sessionID': self.session_id}

    @staticmethod
    def auto_login(email, password_hash):
        """Effettua il login e recupera il sessionID"""
        login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
        payload = {
            'login': email,
            'password': password_hash,
            'worldId': '327',
            'deviceId': 're-panza-brain-v1'
        }
        try:
            response = requests.post(login_url, data=payload, timeout=15)
            if response.status_code == 200:
                data = plistlib.loads(response.content)
                sid = data.get('sessionID')
                if sid:
                    return RePanzaClient(sid)
            return None
        except:
            return None

    def fetch_rankings(self, offset=0, limit=50):
        """Scarica un blocco di classifica del mondo 327"""
        payload = {
            'offset': str(offset),
            'limit': str(limit),
            'type': '(player_rank)',
            'sortBy': '(row.asc)',
            'worldId': '327'
        }
        try:
            res = requests.post(f"{self.base_url}/playerRanks", headers=self.headers, cookies=self.cookies, data=payload)
            if res.status_code == 200:
                return plistlib.loads(res.content)
            return None
        except:
            return None
