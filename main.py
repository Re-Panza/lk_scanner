import os
import json
import requests
import time
import plistlib
from client import RePanzaClient

def run_scanner():
    EMAIL = os.getenv("LK_EMAIL")
    PASSWORD = os.getenv("LK_PASSWORD")
    
    # 1. Login
    client = RePanzaClient.auto_login(EMAIL, PASSWORD)
    if not client:
        return

    # 2. Configurazione Sessione
    session = requests.Session()
    for cookie in client.cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # Usiamo lo User-Agent DESKTOP del client per coerenza
    session.headers.update({
        'User-Agent': client.user_agent,
        'Accept': 'application/x-bplist',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.lordsandknights.com',
        'Referer': 'https://www.lordsandknights.com/'
    })

    # Usiamo l'endpoint che ci hai dato tu (QueryAction)
    # Nota: A volte su Desktop l'URL cambia leggermente, ma proviamo questo che è potente
    url_ranking = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/QueryAction/playerRanks"
    
    all_players = []
    offset = 0
    step = 100
    
    print(f"🚀 Avvio Scansione (SID: {client.session_id[:8]})...")
    time.sleep(5)

    while True:
        try:
            payload = {
                'offset': str(offset),
                'limit': str(step),
                'type': '(player_rank)',
                'sortBy': '(row.asc)',
                'worldId': '327' 
            }
            
            response = session.post(url_ranking, data=payload, timeout=30)
            
            if response.status_code != 200:
                print(f"⚠️ Errore HTTP {response.status_code}")
                # Debug: se fallisce, vediamo cosa dice il server
                print(f"Risposta: {response.text[:200]}")
                break

            try:
                data = plistlib.loads(response.content)
            except:
                print("⚠️ Risposta non è un PLIST valido.")
                break

            players = data.get('playerRanks', [])
            # Fallback per sicurezza
            if not players: players = data.get('rows', [])
            
            if not players:
                print("🏁 Fine lista o nessun dato.")
                break
            
            all_players.extend(players)
            print(f"📥 Scaricati {len(all_players)} giocatori...")
            
            if len(players) < step:
                break
            
            offset += step
            time.sleep(0.5)
            
        except Exception as e:
            print(f"💥 Errore: {e}")
            break

    # 3. Salvataggio
    if all_players:
        clean_data = []
        for p in all_players:
            # Pulizia tipi di dati strani del plist
            clean_p = {k: (str(v) if not isinstance(v, (str, int, float, bool, list, dict, type(None))) else v) for k, v in p.items()}
            clean_data.append(clean_p)

        with open("database_classificamondo327.json", "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=4, ensure_ascii=False)
        
        msg = f"✅ Scansione completata: {len(clean_data)} giocatori."
        print(msg)
        RePanzaClient.send_telegram_alert(msg)
    else:
        print("❌ Nessun dato salvato.")

if __name__ == "__main__":
    run_scanner()
