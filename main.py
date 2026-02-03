import json
import os
import time
import requests
from client import RePanzaClient

# Configurazione Secrets GitHub
EMAIL = os.getenv('LK_EMAIL')
PASS_HASH = os.getenv('LK_PASS_HASH')
TG_TOKEN = os.getenv('TELEGRAM_TOKEN')
TG_ID = os.getenv('TELEGRAM_CHAT_ID')
DATABASE_FILE = "database_classificamondo327.json"

def invia_telegram(msg):
    if TG_TOKEN and TG_ID:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        try:
            requests.post(url, json={'chat_id': TG_ID, 'text': msg})
        except:
            print("Errore Telegram")

def run_scan():
    print("🚀 Re Panza Brain: Inizio Scansione Mondo 327...")
    bot = RePanzaClient.auto_login(EMAIL, PASS_HASH)
    
    if not bot:
        msg = "🚨 RE PANZA ALERT: Login fallito! Account esca bannato o credenziali errate."
        invia_telegram(msg)
        return

    all_players = []
    # Scansioniamo i primi 1000 giocatori (20 blocchi da 50)
    for offset in range(0, 1000, 50):
        print(f"📡 Scaricando offset {offset}...")
        data = bot.fetch_rankings(offset=offset)
        
        if data and 'playerRanks' in data:
            for p in data['playerRanks']:
                all_players.append({
                    'id': p.get('id'),
                    'nome': p.get('nick'),
                    'punti': p.get('currentPoints'),
                    'rank': p.get('rank')
                })
        time.sleep(1.5) # Pausa anti-ban

    if all_players:
        db_content = {
            "last_update": time.strftime('%Y-%m-%d %H:%M:%S'),
            "world": "327",
            "total_players": len(all_players),
            "players": all_players
        }
        with open(DATABASE_FILE, "w", encoding="utf-8") as f:
            json.dump(db_content, f, indent=4, ensure_ascii=False)
        print(f"✅ Scan completato. {len(all_players)} player salvati.")
    else:
        invia_telegram("⚠️ Scan completato ma nessun dato trovato. Controlla il worldID.")

if __name__ == "__main__":
    run_scan()
