import hashlib
import requests
import plistlib

@staticmethod
def auto_login(email, password_raw):
    # La logica di L&K spesso concatena l'email alla password prima dell'hashing
    # Proviamo la combinazione SHA-256 standard del browser
    salted_string = password_raw # Inizia con la pass pulita
    hash_to_send = hashlib.sha256(salted_string.encode('utf-8')).hexdigest()
    
    login_url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
    
    payload = {
        'login': email,
        'password': hash_to_send,
        'worldId': '327',
        'deviceId': 'f5c411a2d7b216ecf64213eb9b62fb77d27fe73fa398d94766c547d553cd05fd',
        'apiVersion': '1.0',
        'platform': 'browser'
    }
    
    headers = {
        'Accept': 'application/x-bplist',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'XYClient-Client': 'lk_b_3',
        'XYClient-Loginclient': 'Chrome',
        'XYClient-Loginclientversion': '10.8.0'
    }

    try:
        print(f"📡 Tentativo Login con SHA-256 di '{password_raw}'...")
        response = requests.post(login_url, data=payload, headers=headers, timeout=30)
        data = plistlib.loads(response.content)
        
        if 'sessionID' in data:
            print("✅ LOGIN RIUSCITO!")
            return data['sessionID']
        else:
            # Se fallisce, il server risponde ancora 'Login does not exist'
            print(f"❌ Errore Server: {data.get('localized', 'Credenziali errate')}")
            return None
    except Exception as e:
        print(f"💥 Errore tecnico: {e}")
        return None
