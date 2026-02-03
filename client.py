import hashlib
import requests
import plistlib

@staticmethod
def auto_login(email, password_raw):
    # Generiamo l'MD5 della password reale. 
    # È il metodo più stabile per i bot su L&K.
    md5_password = hashlib.md5(password_raw.encode('utf-8')).hexdigest()
    
    login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
    
    payload = {
        'login': email,
        'password': md5_password,
        'worldId': '327',
        'deviceId': 'f5c411a2d7b216ecf64213eb9b62fb77d27fe73fa398d94766c547d553cd05fd', # Dal tuo curl
        'apiVersion': '1.0',
        'platform': 'browser'
    }
    
    headers = {
        'Accept': 'application/x-bplist',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'XYClient-Client': 'lk_b_3',
        'XYClient-Loginclient': 'Chrome',
        'XYClient-Loginclientversion': '10.8.0' # Preso dal tuo game.js
    }

    try:
        # Timeout lungo per evitare il 'Read timed out' visto nei log
        response = requests.post(login_url, data=payload, headers=headers, timeout=30)
        data = plistlib.loads(response.content)
        
        if 'sessionID' in data:
            print("✅ LOGIN RIUSCITO!")
            return data['sessionID']
        else:
            print(f"❌ Errore: {data.get('localized', 'Credenziali non riconosciute')}")
            return None
    except Exception as e:
        print(f"💥 Errore tecnico: {e}")
        return None
