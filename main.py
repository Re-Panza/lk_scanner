import os
import json
import requests
import time
from client import RePanzaClient

def run_scanner():
    EMAIL = os.getenv("LK_EMAIL")
    PASSWORD = os.getenv("LK_PASSWORD")
    
    # 1. Login e recupero chiave (SID)
    client = RePanzaClient.auto_login(EMAIL, PASSWORD)
    
    if not client:
        print("❌ SessionID mancante. Stop.")
        return

    # 2. CHIAMATA DIRETTA API (Il "curl" che chiedevi)
    # Questo URL è l'endpoint esatto che il gioco chiama dietro le quinte
    url_ranking = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction/getRanking"
    
    all_players = []
    offset = 0
    step = 100
    
    print(f"🚀 SID Preso! Scarico classifica via API diretta...")
    RePanzaClient.send_telegram_alert("🔮 RePanza Oracle: Login OK. Scarico classifica...")

    while True:
        try:
            # Parametri esatti per farsi dare la classifica
            params = {
                "sessionID": client.session_id,
                "offset": offset,
                "count": step,
                "rankingType": 0 # Classifica Punti
            }
            
            # Richiesta diretta (velocissima)
            response = requests.get(url_ranking, params=params, timeout=20)
            
            if response.status_code != 200:
                print(f"⚠️ Errore API: {response.status_code}")
                break
            
            data = response.json()
            players = data.get('allRankings', [])
            
            if not players:
                break
            
            all_players.extend(players)
            print(f"📥 Scaricati {len(all_players)} player (Offset {offset})...")
            
            if len(players) < step:
                break
                
            offset += step
            time.sleep(0.1) # Massima velocità
            
        except Exception as e:
            print(f"💥 Errore API: {e}")
            break

    # 3. Salvataggio
    if all_players:
        filename = "database_classificamondo327.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_players, f, indent=4, ensure_ascii=False)
        
        msg = f"✅ Scansione completata!\n📊 Giocatori totali: {len(all_players)}"
        print(msg)
        RePanzaClient.send_telegram_alert(msg)

if __name__ == "__main__":
    run_scanner()
