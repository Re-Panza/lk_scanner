import os
from client import RePanzaClient

def run_scan():
    # Recuperiamo i dati dai Secrets di GitHub
    email = os.getenv('LK_EMAIL')
    password = os.getenv('LK_PASSWORD') # Abbiamo cambiato nome qui!

    if not email or not password:
        # Se ricevi ancora l'errore, stampiamo cosa manca (senza mostrare i dati sensibili)
        print(f"🚨 ERRORE: Mancano i dati! Email: {'OK' if email else 'MANCANTE'}, Pass: {'OK' if password else 'MANCANTE'}")
        return

    print(f"🚀 Re Panza Brain: Avvio Scansione Totale Mondo 327 per {email}...")
    
    # Avviamo il login col browser
    bot = RePanzaClient.auto_login(email, password)
    
    if bot:
        # Qui va il resto del tuo codice per scaricare la classifica
        print("✅ Connessione riuscita, procedo con il ranking...")
