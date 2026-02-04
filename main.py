import os
import json
import requests
import time
from client import RePanzaClient

def run_scanner():
    EMAIL = os.getenv("LK_EMAIL")
    PASSWORD = os.getenv("LK_PASSWORD")
    
    client = RePanzaClient.auto_login(EMAIL, PASSWORD)
    if not client:
        print("❌ Impossibile ottenere il sessionID. Esco.")
        return

    # Endpoint Ranking Mondo 327 (Italia VI)
    url_ranking = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction/getRanking"
    all_players = []
    offset = 0
    step = 100
    
    print(f"📊 Avvio scansione con SID: {client.session_id[:8]}...")
    
    while True:
        try:
            params = {
                "sessionID": client.session_id,
                "offset": offset,
                "count": step,
                "rankingType": 0
            }
            response = requests.get(url_ranking, params=params, timeout=15)
            
            if response.status_code == 403:
                RePanzaClient.send_telegram_alert("⚠️ Account bannato durante la scansione!")
                break
            
            data = response.json()
            players = data.get('allRankings', [])
            
            if not players:
                break
            
            all_players.extend(players)
            print(f"📥 Scaricati {len(all_players)} player...")
            
            if len(players) < step: # Fine classifica
                break
                
            offset += step
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ Errore download: {e}")
            break

    # Salvataggio Database
    filename = "database_classificamondo327.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_players, f, indent=4, ensure_ascii=False)
    
    RePanzaClient.send_telegram_alert(f"📊 Scansione Italia VI completata! {len(all_players)} giocatori salvati.")

if __name__ == "__main__":
    run_scanner()
