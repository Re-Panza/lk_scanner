import os
import json
import requests
import time
import plistlib
import re
from playwright.sync_api import sync_playwright

# --- CONFIGURAZIONE ---
SERVER_ID = "LKWorldServer-RE-IT-6"
WORLD_ID = "327"
BACKEND_URL = "https://backend3.lordsandknights.com"
FILE_DATABASE = "database_mondo_327.json"
FILE_HISTORY = "cronologia_327.json"

class RePanzaClient:
    def __init__(self, cookies, user_agent):
        self.cookies = cookies
        self.user_agent = user_agent

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            args = ['--disable-blink-features=AutomationControlled', '--no-sandbox', '--disable-setuid-sandbox', '--disable-infobars']
            
            browser = p.chromium.launch(headless=True, args=args)
            context = browser.new_context(viewport={'width': 1366, 'height': 768}, user_agent=ua)
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            capture = {"logged_in": False}

            def intercept_response(response):
                if "login" in response.url and response.status == 200: capture["logged_in"] = True

            page.on("response", intercept_response)
            
            try:
                print("🌐 Caricamento Lords & Knights...")
                page.goto("https://www.lordsandknights.com/", wait_until="domcontentloaded", timeout=60000)
                try: page.wait_for_selector('input[placeholder="Email"]', state="visible", timeout=10000)
                except: pass

                page.fill('input[placeholder="Email"]', email)
                page.fill('input[placeholder="Password"]', password)
                time.sleep(1)
                page.click('button:has-text("LOG IN")')
                
                selector_mondo = page.locator(".button-game-world--title:has-text('Italia VI')").first
                selector_ok = page.locator("button:has-text('OK')")
                
                print("⏳ Attesa selezione mondo...")
                for i in range(45):
                    if selector_ok.is_visible(): 
                        try: selector_ok.click()
                        except: pass
                    if selector_mondo.is_visible():
                        try: selector_mondo.click(force=True)
                        except: pass
                    
                    cookies = context.cookies()
                    if any(c['name'] == 'sessionID' for c in cookies):
                        print(f"✅ Login Successo! Sessione catturata.")
                        final_cookies = context.cookies()
                        browser.close()
                        return RePanzaClient(final_cookies, ua)
                    time.sleep(1)
            except Exception as e:
                print(f"⚠️ Errore Login: {e}")
            
            browser.close()
            return None

def fetch_ranking(client):
    session = requests.Session()
    for cookie in client.cookies: session.cookies.set(cookie['name'], cookie['value'])
    
    # Headers precisi presi dal tuo CURL
    session.headers.update({
        'User-Agent': client.user_agent,
        'Accept': 'application/x-bplist',
        'Content-Type': 'application/x-www-form-urlencoded',
        'XYClient-Client': 'lk_b_3',
        'XYClient-Loginclient': 'Chrome',
        'XYClient-Loginclientversion': '10.8.0',
        'XYClient-Platform': 'browser',
        'XYClient-Capabilities': 'base,fortress,city,parti%D0%B0l%CE%A4ran%D1%95its,starterpack,requestInformation,partialUpdate,regions,metropolis',
        'Origin': 'https://www.lordsandknights.com',
        'Referer': 'https://www.lordsandknights.com/'
    })

    url_ranking = f"{BACKEND_URL}/XYRALITY/WebObjects/{SERVER_ID}.woa/wa/QueryAction/playerRanks"
    all_players = {}
    offset = 0
    step = 100 
    
    print(f"🚀 Recupero Classifica Nomi...")
    
    while True:
        try:
            payload = {'offset': str(offset), 'limit': str(step), 'type': '(player_rank)', 'sortBy': '(row.asc)', 'worldId': WORLD_ID}
            response = session.post(url_ranking, data=payload, timeout=30)
            
            if response.status_code != 200: 
                print(f"⚠️ Errore Ranking HTTP: {response.status_code}")
                break

            data = plistlib.loads(response.content)
            players = data.get('playerRanks', []) or data.get('rows', [])
            
            if not players: 
                if offset == 0: print("⚠️ Lista giocatori vuota! Controlla WORLD_ID o Headers.")
                break
            
            for p in players:
                # Cerca ID e NOME in tutti i campi possibili
                pid = p.get('playerID') or p.get('p') or p.get('id')
                name = p.get('nick') or p.get('n') or p.get('name')
                
                if pid: all_players[int(pid)] = name
            
            if len(players) < step: break
            offset += step
            time.sleep(0.3)
        except Exception as e:
            print(f"💥 Errore Ranking: {e}")
            break
    
    print(f"✅ Mappati {len(all_players)} nomi giocatori.")
    return all_players

def enrich_db_with_names(db, player_map):
    """
    Funzione cruciale: Scorres tutto il database esistente e aggiunge
    il nome giocatore (pn) se manca, usando la mappa appena scaricata.
    """
    count_updated = 0
    for key, record in db.items():
        pid = record.get('p')
        # Se c'è un ID giocatore valido (diverso da 0) e abbiamo il suo nome in mappa
        if pid and pid != 0:
            nome_nuovo = player_map.get(pid, "Sconosciuto")
            
            # Aggiorna se manca il nome o se è "Sconosciuto" ma ora lo conosciamo
            if 'pn' not in record or record['pn'] == "Sconosciuto":
                if nome_nuovo != "Sconosciuto":
                    record['pn'] = nome_nuovo
                    count_updated += 1
            # Aggiorna comunque per sicurezza (es. cambio nome)
            elif record['pn'] != nome_nuovo and nome_nuovo != "Sconosciuto":
                 record['pn'] = nome_nuovo
                 count_updated += 1
                 
    print(f"♻️  Nomi applicati retroattivamente a {count_updated} castelli nel database.")
    return db

def process_tile(x, y, session, tmp_map, player_map):
    url = f"{BACKEND_URL}/maps/{SERVER_ID}/{x}_{y}.jtile"
    try:
        response = session.get(url, timeout=10)
        if response.status_code != 200: return False
        
        match = re.search(r'\((.*)\)', response.text, re.S)
        if match:
            data = json.loads(match.group(1))
            if 'habitatArray' in data:
                for h in data['habitatArray']:
                    pid = int(h['playerid'])
                    key = f"{h['mapx']}_{h['mapy']}"
                    
                    # Nome giocatore dalla mappa
                    nome_giocatore = player_map.get(pid, "Sconosciuto")
                    
                    tmp_map[key] = {
                        'p': pid,                   # ID Giocatore
                        'pn': nome_giocatore,       # NOME Giocatore
                        'a': int(h['allianceid']),
                        'n': h.get('name', ''),
                        'x': int(h['mapx']),
                        'y': int(h['mapy']),
                        'pt': int(h['points']),
                        't': int(h['habitattype']),
                        'd': int(time.time())
                    }
                return True
    except: pass
    return False

def run_inactivity_check(data):
    for key, h in data.items():
        if not h.get('p') or h['p'] == 0: continue
        firma = f"{h['n']}|{h['pt']}"
        h['d'] = int(h['d'])
        
        if 'u' not in h: h['u'] = h['d']; h['f'] = firma; continue
        try: last = int(h['u'])
        except: last = h['d']

        if h.get('f') != firma:
            h['u'] = h['d']; h['f'] = firma; h['i'] = False
        else:
            if (h['d'] - last) >= 86400: h['i'] = True
    return data

def run_history_check(old_data, current_player_map, current_map, history_file):
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f: history = json.load(f)
        except: pass

    last_known = {}
    for h in old_data:
        if h.get('p'): last_known[h['p']] = {'n': h.get('pn'), 'a': h.get('a')}

    now = int(time.time())
    new_events = []
    
    if current_player_map:
        for pid, name in current_player_map.items():
            if pid in last_known:
                old = last_known[pid]['n']
                if old and old != "Sconosciuto" and old != name:
                    new_events.append({"type": "name", "p": pid, "old": old, "new": name, "d": now})

    if new_events:
        history.extend(new_events)
        with open(history_file, 'w', encoding='utf-8') as f: json.dump(history[-1000:], f, indent=2)

def run_unified_scanner():
    # Inizializzazione file
    if not os.path.exists(FILE_DATABASE):
        with open(FILE_DATABASE, 'w') as f: json.dump([], f)
    
    EMAIL = os.getenv("LK_EMAIL")
    PASSWORD = os.getenv("LK_PASSWORD")
    
    player_map = {}
    if EMAIL and PASSWORD:
        client = RePanzaClient.auto_login(EMAIL, PASSWORD)
        if client: 
            player_map = fetch_ranking(client)
        else: 
            print("⚠️ Login fallito. Nomi giocatori non disponibili.")
    
    # Carica DB Esistente
    temp_map = {}
    if os.path.exists(FILE_DATABASE):
        try:
            with open(FILE_DATABASE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for entry in data: temp_map[f"{entry['x']}_{entry['y']}"] = entry
        except: pass

    print(f"📂 Database caricato: {len(temp_map)} castelli.")
    
    # --- NUOVO STEP: ARRICCHIMENTO ---
    # Applichiamo subito i nomi scaricati ai dati vecchi
    if player_map and temp_map:
        temp_map = enrich_db_with_names(temp_map, player_map)
    # ---------------------------------

    print(f"🛰️ Avvio Scansione Mappa...")
    session = requests.Session()
    
    punti_caldi = {}
    for entry in temp_map.values():
        tx, ty = entry['x'] // 32, entry['y'] // 32
        punti_caldi[f"{tx}_{ty}"] = (tx, ty)

    for tx, ty in punti_caldi.values():
        process_tile(tx, ty, session, temp_map, player_map)

    # Espansione (Semplificata)
    centerX, centerY = 503, 503
    if temp_map:
        vals = list(temp_map.values())
        if vals:
            centerX = sum(e['x']//32 for e in vals) // len(vals)
            centerY = sum(e['y']//32 for e in vals) // len(vals)

    vuoti = 0
    for r in range(150):
        trovato = False
        xMin, xMax = centerX - r, centerX + r
        yMin, yMax = centerY - r, centerY + r
        punti = []
        for i in range(xMin, xMax + 1): punti.append((i,yMin)); punti.append((i,yMax))
        for j in range(yMin + 1, yMax): punti.append((xMin,j)); punti.append((xMax,j))
        
        for px, py in punti:
            if f"{px}_{py}" not in punti_caldi:
                if process_tile(px, py, session, temp_map, player_map): trovato = True
                punti_caldi[f"{px}_{py}"] = (px, py)
        
        if trovato: vuoti = 0
        else: vuoti += 1
        if vuoti >= 5: break

    # Salvataggio Finale
    temp_map = run_inactivity_check(temp_map)
    run_history_check(list(temp_map.values()), player_map, temp_map, FILE_HISTORY)
    
    final_list = [v for v in temp_map.values() if v['d'] > (time.time() - 259200)]

    print(f"💾 Salvataggio {len(final_list)} record COMPLETI DI NOMI...")
    with open(FILE_DATABASE, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
    
    print("✅ Scansione Completata.")

if __name__ == "__main__":
    run_unified_scanner()
