import os
import json
import requests
import time
from client import RePanzaClient

def run_scanner():
    EMAIL = os.getenv("LK_EMAIL")
    PASSWORD = os.getenv("LK_PASSWORD")
    
    # 1. Otteniamo la chiave di accesso (SID)
    client = RePanzaClient.auto_login(EMAIL, PASSWORD)
    
    if not client:
        print("❌ Impossibile procedere senza SessionID.")
        return

    # 2. CHIAMATA DIRETTA ALL'API (Senza navigazione browser)
    # Questo è l'endpoint corretto per Italia VI
    url_ranking = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction/getRanking"
    
    all_players = []
    offset = 0
    step = 100 # Il server accetta blocchi da 100
    
    print(f"🚀 Avvio download diretto classifica tramite API (SID: {client.session_id[:8]})...")
    RePanzaClient.send_telegram_alert("🔮 RePanza Oracle: Login effettuato. Scarico la classifica via API...")

    while True:
        try:
            # Costruiamo la richiesta "fingendoci" il gioco
            params = {
                "sessionID": client.session_id,
                "offset": offset,
                "count": step,
                "rankingType": 0 # 0 = Classifica Punti, 1 = Offensiva, ecc.
            }
            
            # Richiesta HTTP diretta
            response = requests.get(url_ranking, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"⚠️ Errore API: {response.status_code}")
                break
            
            data = response.json()
            players = data.get('allRankings', [])
            
            if not players:
                print("✅ Fine della classifica raggiunta.")
                break
            
            all_players.extend(players)
            print(f"📥 Scaricati giocatori da {offset} a {offset + len(players)}...")
            
            if len(players) < step:
                break
                
            offset += step
            time.sleep(0.2) # Breve pausa per gentilezza verso il server
            
        except Exception as e:
            print(f"💥 Errore durante il download API: {e}")
            break

    # 3. Salvataggio
    if all_players:
        filename = "database_classificamondo327.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_players, f, indent=4, ensure_ascii=False)
        
        msg = f"✅ Scansione completata!\n📊 Giocatori nel DB: {len(all_players)}"
        print(msg)
        RePanzaClient.send_telegram_alert(msg)
    else:
        print("⚠️ Nessun dato scaricato.")

if __name__ == "__main__":
    run_scanner()
