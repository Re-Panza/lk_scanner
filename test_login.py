import requests
import plistlib
import os

# Recupera i dati dai Secrets (o mettili a mano per un test veloce, ma meglio i Secrets)
EMAIL = os.getenv('LK_EMAIL')
PASS_HASH = os.getenv('LK_PASS_HASH')

def test_login():
    url = "https://login.lordsandknights.com/XYRALITY/WebObjects/BKLoginServer.woa/wa/LoginAction/checkValidLoginBrowser"
    
    payload = {
        'login': EMAIL.strip(), # Rimuove eventuali spazi invisibili
        'password': PASS_HASH.strip(),
        'worldId': '327',
        'deviceId': 'test-device'
    }
    
    headers = {
        'Accept': 'application/x-bplist',
        'User-Agent': 'LordsAndKnights/9.4.2 (iPhone; iOS 16.0)'
    }

    print(f"--- TEST DI DEBUG RE PANZA ---")
    print(f"📧 Email utilizzata: {EMAIL}")
    print(f"🔑 Password Hash (primi 5 caratteri): {PASS_HASH[:5]}...")
    
    try:
        # Test 1: POST standard (Form-data)
        print("\n🧪 Test 1: Invio come Form-Data...")
        r1 = requests.post(url, data=payload, headers=headers)
        print(f"Status: {r1.status_code}")
        try:
            res1 = plistlib.loads(r1.content)
            print(f"Risposta: {res1}")
        except:
            print("Impossibile decodificare la risposta come plist.")

        # Test 2: Inclusione di parametri extra (spesso necessari per account nuovi)
        print("\n🧪 Test 2: Aggiunta parametri platform...")
        payload['platform'] = 'iPhone'
        payload['bundleId'] = 'com.xyrality.lordsandknights'
        r2 = requests.post(url, data=payload, headers=headers)
        print(f"Risposta: {plistlib.loads(r2.content)}")

    except Exception as e:
        print(f"💥 Errore durante il test: {e}")

if __name__ == "__main__":
    test_login()
