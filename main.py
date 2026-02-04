import os
import json
import requests
import time
from client import RePanzaClient

def run_scanner():
    EMAIL = os.getenv("LK_EMAIL")
    PASSWORD = os.getenv("LK_PASSWORD")
    
    # 1. Login Automatico
    client = RePanzaClient.auto_login(EMAIL, PASSWORD)
    if not client:
        return

    # 2. Setup della Sessione "Clonata" (La logica manuale applicata all'automazione)
    session = requests.Session()
    
    # Carichiamo i cookie presi da Playwright dentro requests
    for cookie in client.cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # Header che imitano perfettamente il browser (fondamentale!)
    session.headers.update({
        "User-Agent": client.user_agent,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.lordsandknights.com/"
    })

    # URL API Browser per Italia VI (IT-6)
    url_ranking = "https://backend3.lordsandknights.com/XYRALITY/WebObjects/LKWorldServer-RE-IT-6.woa/wa/PlayerAction/getRanking"
    
    all_players = []
    offset = 0
    step = 100
    
    print(f"🚀 Avvio scaricamento dati (Sessione Browser Autenticata)...")
    time.sleep(5) # Pausa tattica post-login

    while True:
        try:
            params = {
                "sessionID": client.session_id,
                "offset": offset,
                "count": step,
                "rankingType": 0
            }
            
            # Richiesta API usando la sessione coi cookie
            response = session.get(url_ranking, params=params, timeout=30)
            
            # Controllo se è JSON valido
            try:
                data = response.json()
            except ValueError:
                # Se fallisce qui, stampiamo l'HTML per debug
                print(f"⚠️ Risposta Server non valida (HTML): {response.text[:100]}...")
                break

            players = data.get('allRankings', [])
            if not players:
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
        filename = "database_classificamondo327.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_players, f, indent=4, ensure_ascii=False)
        msg = f"✅ Scansione completata: {len(all_players)} giocatori salvati."
        print(msg)
        RePanzaClient.send_telegram_alert(msg)
    else:
        print("❌ Nessun dato salvato.")

if __name__ == "__main__":
    run_scanner()
