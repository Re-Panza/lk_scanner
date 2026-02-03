import json
import os
import time
import random
import requests
from client import RePanzaClient

# --- CONFIGURAZIONE (Recuperata dai Secrets di GitHub) ---
EMAIL = os.getenv('LK_EMAIL')
PASS_HASH = os.getenv('LK_PASS_HASH')
TG_TOKEN = os.getenv('TELEGRAM_TOKEN')
TG_ID = os.getenv('TELEGRAM_CHAT_ID')
DATABASE_FILE = "database_classificamondo327.json"

def invia_telegram(msg):
    """Invia una notifica sul tuo cellulare tramite il Bot Telegram"""
    if TG_TOKEN and TG_ID:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {
            'chat_id': TG_ID,
            'text': msg,
            'parse_mode': 'Markdown'
        }
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Errore nell'invio del messaggio Telegram: {e}")

def run_scan():
    print("🚀 Re Panza Brain: Avvio Scansione Totale Mondo 327...")
    
    # 1. TENTATIVO DI LOGIN
    bot = RePanzaClient.auto_login(EMAIL, PASS_HASH)
    
    if not bot:
        errore_msg = "🚨 *RE PANZA ALERT*\nLogin fallito! L'account esca potrebbe essere bannato o le credenziali nei Secrets sono errate."
        print(errore_msg)
        invia_telegram(errore_msg)
        return

    all_players = []
    offset = 0
    limit = 50
    
    # 2. CICLO DI SCANSIONE INFINITO
    try:
        while True:
            print(f"📡 Scaricando classifica: offset {offset}...")
            data = bot.fetch_rankings(offset=offset, limit=limit)
            
            # Controllo se abbiamo dati validi
            if not data or 'playerRanks' not in data:
                print("⚠️ Risposta del server non valida o vuota.")
                break
            
            giocatori_ricevuti = data['playerRanks']
            
            # Se la lista è vuota, abbiamo raggiunto la fine della classifica
            if len(giocatori_ricevuti) == 0:
                print("🏁 Fine classifica raggiunta con successo.")
                break
                
            for p in giocatori_ricevuti:
                all_players.append({
                    'id': p.get('id'),
                    'nome': p.get('nick'),
                    'punti': p.get('currentPoints'),
                    'rank': p.get('rank')
                })
            
            # Incrementiamo l'offset per il prossimo blocco
            offset += limit
            
            # PAUSA VARIABILE: Aspetta un tempo casuale tra 1.2 e 2.8 secondi
            # Questo simula un comportamento umano che non clicca con precisione millimetrica
            attesa = random.uniform(1.2, 2.8)
            time.sleep(attesa)

        # 3. SALVATAGGIO DATI
        if all_players:
            db_content = {
                "last_update": time.strftime('%Y-%m-%d %H:%M:%S'),
                "world": "327",
                "total_players": len(all_players),
                "players": all_players
            }
            
            with open(DATABASE_FILE, "w", encoding="utf-8") as f:
                json.dump(db_content, f, indent=4, ensure_ascii=False)
            
            success_msg = f"✅ *Scan Completato*\nMondo: 327\nGiocatori salvati: {len(all_players)}\nDatabase aggiornato."
            print(success_msg)
            # Inviamo la notifica di successo solo se è il primo scan o se vuoi conferma
            # invia_telegram(success_msg) 
        else:
            invia_telegram("⚠️ Scan terminato, ma non è stato possibile recuperare alcun giocatore.")

    except Exception as e:
        errore_generico = f"❌ *Errore critico durante lo scan*:\n`{str(e)}`"
        print(errore_generico)
        invia_telegram(errore_generico)

if __name__ == "__main__":
    run_scan()
