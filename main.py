import os
import sys
from client import RePanzaClient

def run_scan():
    # Recuperiamo i dati dai Secrets di GitHub
    email = os.getenv('LK_EMAIL')
    password = os.getenv('LK_PASSWORD')

    if not email or not password:
        print(f"🚨 ERRORE: Mancano i dati! Email: {'OK' if email else 'MANCANTE'}, Pass: {'OK' if password else 'MANCANTE'}")
        return

    print(f"🚀 Re Panza Brain: Avvio Scansione Totale Mondo 327 per {email}...")
    
    try:
        # Avviamo il login col browser simulato
        bot = RePanzaClient.auto_login(email, password)
        
        if bot:
            print("✅ Connessione riuscita! Inizio recupero dati...")
            # Qui aggiungi la tua logica per scaricare i dati
        else:
            print("❌ Login fallito: Il browser non ha catturato la sessione.")
    except Exception as e:
        print(f"💥 Errore durante l'esecuzione: {e}")

# QUESTA PARTE È FONDAMENTALE PER FARLO PARTIRE
if __name__ == "__main__":
    run_scan()
