import os
import json
import requests
import time
import plistlib # FONDAMENTALE PER LEGGERE LA RISPOSTA
from client import RePanzaClient

def run_scanner():
    EMAIL = os.getenv("LK_EMAIL")
    PASSWORD = os.getenv("LK_PASSWORD")
    
    # 1. Login
    client = RePanzaClient.auto_login(EMAIL, PASSWORD)
    if not client:
        return

    # 2. Configurazione Sessione Clone
    session = requests.Session()
    for cookie in client.cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # HEADER COPIATI DAL TUO CURL
    session.headers.update({
        'User-Agent': client.user_agent,
        'Accept': 'application/x-bplist', # Questo è il segreto!
        'Content-Type': 'application/x-www-form-urlencoded',
        'XYClient-Client': 'lk_b_3',
        'XYClient-Platform': 'browser',
        'XYClient-PlatformLanguage': 'it',
        'Origin': 'https://www.lordsandknights.com',
        'Referer': 'https://www.lordsandknights.com/'
    })

    # URL ESATTO DAL CURL
    url_ranking = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/QueryAction/playerRanks"
    
    all_players = []
    offset = 0
    step = 100
    
    print(f"🚀 Avvio Scansione BPLIST (SID: {client.session_id[:8]})...")
    time.sleep(5)

    while True:
        try:
            # PAYLOAD COSTRUITO SULLA BASE DEL CURL
            # Sostituiamo 'centerOnPage...' con 'offset' per scorrere la lista
            payload = {
                'offset': str(offset),
                'limit': str(step),
                'type': '(player_rank)',
                'sortBy': '(row.asc)',
                'worldId': '327' # Mondo Italia VI
            }
            
            # Richiesta POST (Il curl usa --data-raw, quindi è una POST)
            response = session.post(url_ranking, data=payload, timeout=30)
            
            if response.status_code != 200:
                print(f"⚠️ Errore HTTP {response.status_code}")
                break

            # DECODIFICA PLIST BINARIO
            try:
                data = plistlib.loads(response.content)
            except Exception as e:
                print(f"⚠️ Errore decodifica PLIST: {e}")
                # Se fallisce, stampiamo l'inizio per capire
                print(f"Risposta raw: {response.content[:100]}")
                break

            # L'app di solito restituisce 'playerRanks' o 'rows'
            players = data.get('playerRanks', [])
            if not players:
                # Fallback: a volte la chiave cambia
                players = data.get('rows', [])
            
            if not players:
                print("🏁 Nessun altro giocatore trovato.")
                break
            
            all_players.extend(players)
            print(f"📥 Scaricati {len(all_players)} giocatori...")
            
            if len(players) < step:
                break
            
            offset += step
            time.sleep(0.5)
            
        except Exception as e:
            print(f"💥 Errore Critico: {e}")
            break

    # 3. Salvataggio e Conversione in JSON Leggibile
    if all_players:
        filename = "database_classificamondo327.json"
        
        # Pulizia dati (i plist possono contenere oggetti binari non serializzabili in JSON)
        clean_data = []
        for p in all_players:
            # Convertiamo eventuali byte/date in stringhe
            clean_p = {k: (str(v) if not isinstance(v, (str, int, float, bool, list, dict, type(None))) else v) for k, v in p.items()}
            clean_data.append(clean_p)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=4, ensure_ascii=False)
        
        msg = f"✅ Scansione BPLIST completata: {len(clean_data)} giocatori."
        print(msg)
        RePanzaClient.send_telegram_alert(msg)
    else:
        print("❌ Nessun dato salvato.")

if __name__ == "__main__":
    run_scanner()
