import os
import json
import requests
import time
from client import RePanzaClient

# Credenziali dalle Secret di GitHub
EMAIL = os.getenv("LK_EMAIL")
PASSWORD = os.getenv("LK_PASSWORD")

def run_scanner():
    # 1. Otteniamo il SessionID tramite Playwright
    client = RePanzaClient.auto_login(EMAIL, PASSWORD)
    
    if not client:
        print("❌ Impossibile ottenere il sessionID. Esco.")
        return

    # 2. Configurazione Scansione Classifica Mondo 327
    url_ranking = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction/getRanking"
    all_players = []
    offset = 0
    step = 100
    
    print(f"📊 Avvio scansione classifica totale...")
    
    while True:
        params = {
            "sessionID": client.session_id,
            "offset": offset,
            "count": step,
            "rankingType": 0
        }
        
        try:
            response = requests.get(url_ranking, params=params)
            data = response.json()
            # La struttura tipica restituisce la lista in 'allRankings'
            players = data.get('allRankings', [])
            
            if not players:
                break
            
            all_players.extend(players)
            print(f"📥 Scaricati {len(all_players)} giocatori...")
            
            if len(players) < step: # Fine della classifica
                break
                
            offset += step
            time.sleep(0.3) # Rispetto per il server
            
        except Exception as e:
            print(f"⚠️ Errore durante il download: {e}")
            break

    # 3. Salvataggio Database
    filename = "database_classificamondo327.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_players, f, indent=4, ensure_ascii=False)
    
    print(f"💾 DATABASE AGGIORNATO: {len(all_players)} player salvati in {filename}!")

if __name__ == "__main__":
    run_scanner()
