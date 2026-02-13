import os
import json
import requests
import time
import plistlib
import re
import copy # Utilizzato per fare la "fotografia" del database prima della scansione
from playwright.sync_api import sync_playwright

# --- CONFIGURAZIONE ---
SERVER_ID = "LKWorldServer-RE-IT-6"
WORLD_ID = "327"
WORLD_NAME = "Italia VI" # Nome esatto del bottone del mondo
BACKEND_URL = "https://backend3.lordsandknights.com"
FILE_DATABASE = "database_mondo_327.json"
FILE_HISTORY = "cronologia_327.json"

def send_telegram_alert(world_name):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("⚠️ Credenziali Telegram mancanti nei secrets. Impossibile inviare notifica.")
        return
        
    messaggio = f"Capo, il mondo '{world_name}' forse è stato bannato, controlla."
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": messaggio})
        if response.status_code == 200:
            print("📲 Notifica Telegram inviata con successo!")
        else:
            print(f"⚠️ Errore API Telegram: {response.text}")
    except Exception as e:
        print(f"⚠️ Errore invio notifica Telegram: {e}")

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
                
                selector_mondo = page.locator(f".button-game-world--title:has-text('{WORLD_NAME}')").first
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

def fetch_alliance_ranking(client):
    session = requests.Session()
    for cookie in client.cookies: session.cookies.set(cookie['name'], cookie['value'])
    
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

    url_ranking = f"{BACKEND_URL}/XYRALITY/WebObjects/{SERVER_ID}.woa/wa/QueryAction/allianceRanks"
    all_alliances = {}
    offset = 0
    step = 100 
    
    print(f"🚀 Recupero Classifica Alleanze...")
    
    while True:
        try:
            payload = {'offset': str(offset), 'limit': str(step), 'type': '(alliance_rank)', 'sortBy': '(row.asc)', 'worldId': WORLD_ID}
            response = session.post(url_ranking, data=payload, timeout=30)
            
            if response.status_code != 200: 
                print(f"⚠️ Errore Ranking Alleanze HTTP: {response.status_code}")
                break

            data = plistlib.loads(response.content)
            alliances = data.get('allianceRanks', []) or data.get('rows', [])
            
            if not alliances: 
                break
            
            for a in alliances:
                aid = a.get('allianceID') or a.get('a') or a.get('id')
                name = a.get('name') or a.get('n')
                
                if aid: all_alliances[int(aid)] = name
            
            if len(alliances) < step: break
            offset += step
            time.sleep(0.3)
        except Exception as e:
            print(f"💥 Errore Ranking Alleanze: {e}")
            break
    
    print(f"✅ Mappate {len(all_alliances)} alleanze.")
    return all_alliances

def enrich_db_with_names(db, player_map, alliance_map):
    count_updated = 0
    for key, record in db.items():
        pid = record.get('p')
        if pid and pid != 0:
            nome_nuovo = player_map.get(pid, "Sconosciuto")
            
            if 'pn' not in record or record['pn'] == "Sconosciuto":
                if nome_nuovo != "Sconosciuto":
                    record['pn'] = nome_nuovo
                    count_updated += 1
            elif record['pn'] != nome_nuovo and nome_nuovo != "Sconosciuto":
                 record['pn'] = nome_nuovo
                 count_updated += 1
                 
        aid = record.get('a')
        if aid and aid != 0:
            nome_alleanza = alliance_map.get(aid, "")
            if 'an' not in record or record['an'] == "":
                if nome_alleanza:
                    record['an'] = nome_alleanza
            elif record['an'] != nome_alleanza and nome_alleanza != "":
                 record['an'] = nome_alleanza
                 
    print(f"♻️ Nomi e Alleanze applicati retroattivamente a {count_updated} castelli nel database.")
    return db

def process_tile(x, y, session, tmp_map, player_map, alliance_map):
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
                    
                    nome_giocatore = player_map.get(pid, "Sconosciuto")
                    aid = int(h['allianceid'])
                    nome_alleanza = alliance_map.get(aid, "")
                    
                    tmp_map[key] = {
                        'p': pid,                   
                        'pn': nome_giocatore,       
                        'a': aid,
                        'an': nome_alleanza,  # Inserito il nome alleanza sotto pn
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
        firma = f"{h.get('pn', 'Sconosciuto')}|{h.get('a', 0)}|{h['n']}|{h['pt']}"
        h['d'] = int(h['d'])
        
        if 'u' not in h: h['u'] = h['d']; h['f'] = firma; continue
        try: last = int(h['u'])
        except: last = h['d']

        if h.get('f') != firma:
            h['u'] = h['d']; h['f'] = firma; h['i'] = False
        else:
            if (h['d'] - last) >= 86400: h['i'] = True
    return data

def run_history_check(old_db_list, new_db_list, history_file):
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f: 
                history = json.load(f)
        except: pass

    last_known = {}
    for h in old_db_list:
        pid = h.get('p')
        if pid and pid != 0:
            if pid not in last_known:
                last_known[pid] = {'n': h.get('pn', 'Sconosciuto'), 'a': h.get('a', 0), 'an': h.get('an', '')}

    current_known = {}
    for h in new_db_list:
        pid = h.get('p')
        if pid and pid != 0:
            if pid not in current_known:
                current_known[pid] = {'n': h.get('pn', 'Sconosciuto'), 'a': h.get('a', 0), 'an': h.get('an', '')}

    now = int(time.time())
    new_events = []

    for pid, new_data in current_known.items():
        if pid in last_known:
            old_data = last_known[pid]
            
            old_name = old_data['n']
            new_name = new_data['n']
            if old_name and old_name != "Sconosciuto" and new_name and new_name != "Sconosciuto" and old_name != new_name:
                new_events.append({"type": "name", "p": pid, "old": old_name, "new": new_name, "d": now})
                print(f"📜 CRONOLOGIA: Giocatore {pid} ha cambiato nome da '{old_name}' a '{new_name}'")
            
            old_ally = old_data['a']
            new_ally = new_data['a']
            if old_ally != new_ally:
                new_events.append({
                    "type": "alliance", 
                    "p": pid, 
                    "old": old_ally, 
                    "new": new_ally, 
                    "old_name": old_data['an'], 
                    "new_name": new_data['an'], 
                    "d": now
                })
                print(f"📜 CRONOLOGIA: Giocatore {pid} ha cambiato alleanza da {old_ally} ({old_data['an']}) a {new_ally} ({new_data['an']})")

    if new_events:
        history.extend(new_events)
        with open(history_file, 'w', encoding='utf-8') as f: 
            json.dump(history[-5000:], f, indent=2)

def run_unified_scanner():
    if not os.path.exists(FILE_DATABASE):
        with open(FILE_DATABASE, 'w') as f: json.dump([], f)
    
    EMAIL = os.getenv("LK_EMAIL")
    PASSWORD = os.getenv("LK_PASSWORD")
    
    player_map = {}
    alliance_map = {}
    if EMAIL and PASSWORD:
        client = RePanzaClient.auto_login(EMAIL, PASSWORD)
        if client: 
            player_map = fetch_ranking(client)
            alliance_map = fetch_alliance_ranking(client)
        else: 
            print("⚠️ Login fallito. Nomi giocatori e alleanze non disponibili.")
            send_telegram_alert(WORLD_NAME)
    
    temp_map = {}
    if os.path.exists(FILE_DATABASE):
        try:
            with open(FILE_DATABASE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for entry in data: temp_map[f"{entry['x']}_{entry['y']}"] = entry
        except: pass

    print(f"📂 Database caricato: {len(temp_map)} castelli.")
    
    # --- SNAPSHOT PRE-SCANSIONE PER CRONOLOGIA ---
    old_db_list = copy.deepcopy(list(temp_map.values()))

    if player_map and temp_map:
        temp_map = enrich_db_with_names(temp_map, player_map, alliance_map)

    print(f"🛰️ Avvio Scansione Mappa...")
    session = requests.Session()
    
    punti_caldi = {}
    for entry in temp_map.values():
        tx, ty = entry['x'] // 32, entry['y'] // 32
        punti_caldi[f"{tx}_{ty}"] = (tx, ty)

    for tx, ty in punti_caldi.values():
        process_tile(tx, ty, session, temp_map, player_map, alliance_map)

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
                if process_tile(px, py, session, temp_map, player_map, alliance_map): trovato = True
                punti_caldi[f"{px}_{py}"] = (px, py)
        
        if trovato: vuoti = 0
        else: vuoti += 1
        if vuoti >= 5: break

    temp_map = run_inactivity_check(temp_map)
    
    # --- CONTROLLO CRONOLOGIA CON DATI NUOVI ---
    new_db_list = list(temp_map.values())
    run_history_check(old_db_list, new_db_list, FILE_HISTORY)
    
    final_list = [v for v in temp_map.values() if v['d'] > (time.time() - 259200)]

    print(f"💾 Salvataggio {len(final_list)} record COMPLETI DI NOMI E ALLEANZE...")
    with open(FILE_DATABASE, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
    
    print("✅ Scansione Completata.")

if __name__ == "__main__":
    run_unified_scanner()
