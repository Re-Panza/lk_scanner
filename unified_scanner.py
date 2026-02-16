import os
import json
import requests
import time
import plistlib
import re
import copy 
import random 
from playwright.sync_api import sync_playwright

# --- CONFIGURAZIONE ---
SERVER_ID = "LKWorldServer-RE-IT-6"
WORLD_ID = "327"
WORLD_NAME = "Italia VI" 
BACKEND_URL = "https://backend3.lordsandknights.com"
FILE_DATABASE = "database_mondo_327.json"
FILE_HISTORY = "cronologia_327.json"

def send_telegram_alert(world_name):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id: return
    messaggio = f"Capo, il login per '{world_name}' è fallito. La mappa è stata aggiornata, ma i nomi e i nuovi ID non sono stati scaricati. Controlla lo screenshot su GitHub!"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try: requests.post(url, json={"chat_id": chat_id, "text": messaggio})
    except: pass

class RePanzaClient:
    def __init__(self, cookies, user_agent):
        self.cookies = cookies
        self.user_agent = user_agent

    @staticmethod
    def auto_login(email, password):
        print("\n🔑 Inizio procedura di Login Sicuro con Playwright...")
        with sync_playwright() as p:
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            args = ['--disable-blink-features=AutomationControlled', '--no-sandbox']
            browser = p.chromium.launch(headless=True, args=args)
            context = browser.new_context(user_agent=ua)
            page = context.new_page()
            try:
                page.goto("https://www.lordsandknights.com/", timeout=120000)
                time.sleep(random.uniform(1.5, 3.0))
                
                try: page.wait_for_selector('input[placeholder="Email"]', state="visible", timeout=10000)
                except: pass

                page.type('input[placeholder="Email"]', email, delay=random.randint(50, 150))
                time.sleep(random.uniform(0.3, 0.8))
                page.type('input[placeholder="Password"]', password, delay=random.randint(50, 150))
                time.sleep(random.uniform(0.5, 1.2))
                page.click('button:has-text("LOG IN")')
                
                selector_mondo = page.locator(f".button-game-world--title:has-text('{WORLD_NAME}')").first
                selector_ok = page.locator("button:has-text('OK')")
                
                start_time = time.time()
                while time.time() - start_time < 600:
                    if selector_ok.is_visible(): 
                        try: 
                            time.sleep(random.uniform(0.5, 1.0))
                            selector_ok.click()
                        except: pass
                    if selector_mondo.is_visible():
                        try: 
                            time.sleep(random.uniform(0.8, 1.5))
                            selector_mondo.click(force=True)
                        except: pass
                    
                    cookies = context.cookies()
                    if any(c['name'] == 'sessionID' for c in cookies):
                        print(f"✅ Login Successo! Sessione catturata.")
                        final_cookies = context.cookies()
                        browser.close()
                        return RePanzaClient(final_cookies, ua)
                    time.sleep(random.uniform(0.8, 1.3))
                
                print("🛑 Timeout di 10 minuti raggiunto senza riuscire a loggare.")
                try: page.screenshot(path="debug_login_error.png", full_page=True)
                except: pass

            except Exception as e:
                print(f"⚠️ Errore Login: {e}")
                try: page.screenshot(path="debug_login_error.png", full_page=True)
                except: pass
            
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

    url = f"{BACKEND_URL}/XYRALITY/WebObjects/{SERVER_ID}.woa/wa/QueryAction/playerRanks"
    all_players = {}
    offset = 0
    print(f"🚀 Recupero Classifica Nomi...")
    while True:
        payload = {'offset': str(offset), 'limit': '100', 'type': '(player_rank)', 'worldId': WORLD_ID}
        try:
            res = session.post(url, data=payload, timeout=20)
            if res.status_code != 200: break
            data = plistlib.loads(res.content)
            players = data.get('playerRanks', []) or data.get('rows', [])
            if not players: break
            for p in players:
                pid = p.get('playerID') or p.get('p') or p.get('id')
                name = p.get('nick') or p.get('n') or p.get('name')
                if pid: all_players[int(pid)] = name
            offset += 100
            time.sleep(random.uniform(0.4, 1.1))
        except: break
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

    url = f"{BACKEND_URL}/XYRALITY/WebObjects/{SERVER_ID}.woa/wa/QueryAction/allianceRanks"
    all_alliances = {}
    offset = 0
    print(f"🚀 Recupero Classifica Alleanze...")
    while True:
        payload = {'offset': str(offset), 'limit': '100', 'type': '(alliance_rank)', 'worldId': WORLD_ID}
        try:
            res = session.post(url, data=payload, timeout=20)
            if res.status_code != 200: break
            data = plistlib.loads(res.content)
            alliances = data.get('allianceRanks', []) or data.get('rows', [])
            if not alliances: break
            for a in alliances:
                aid = a.get('allianceID') or a.get('a') or a.get('id')
                name = a.get('name') or a.get('n')
                if aid: all_alliances[int(aid)] = name
            offset += 100
            time.sleep(random.uniform(0.4, 1.1))
        except: break
    print(f"✅ Mappate {len(all_alliances)} alleanze.")
    return all_alliances

def process_tile_public(x, y, session, tmp_map):
    """Scansione JTILE Pubblica (Senza Login). Non inserisce i nomi."""
    url = f"{BACKEND_URL}/maps/{SERVER_ID}/{x}_{y}.jtile"
    try:
        time.sleep(random.uniform(0.05, 0.15))
        response = session.get(url, timeout=10)
        if response.status_code != 200: return False
        
        start = response.text.find('(')
        end = response.text.rfind(')')
        
        if start != -1 and end != -1:
            data = json.loads(response.text[start+1:end])
            if 'habitatArray' in data:
                for h in data['habitatArray']:
                    pid = int(h['playerid'])
                    key = f"{h['mapx']}_{h['mapy']}"
                    
                    if key in tmp_map:
                        tmp_map[key].update({
                            'p': pid,
                            'a': int(h['allianceid']),
                            'n': h.get('name', ''),
                            'pt': int(h['points']),
                            't': int(h['habitattype']),
                            'd': int(time.time())
                        })
                    else:
                        tmp_map[key] = {
                            'p': pid, 'pn': "Sconosciuto",
                            'a': int(h['allianceid']), 'an': "",
                            'n': h.get('name', ''),
                            'x': int(h['mapx']), 'y': int(h['mapy']),
                            'pt': int(h['points']), 't': int(h['habitattype']),
                            'd': int(time.time())
                        }
                return True
    except: pass
    return False

def extract_hidden_ids(node, known_map, found_set):
    if isinstance(node, dict):
        hx = node.get('x') or node.get('mapX') or node.get('mapx')
        hy = node.get('y') or node.get('mapY') or node.get('mapy')
        
        if hx is not None and hy is not None:
            try:
                hid = node.get('id') or node.get('habitatID') or node.get('primaryKey')
                if hid:
                    key = f"{int(hx)}_{int(hy)}"
                    if key in known_map:
                        known_map[key]['id_habitat'] = hid
                        found_set.add(key)
            except: pass
        
        for k, v in node.items():
            if isinstance(v, dict):
                sub_hx = v.get('x') or v.get('mapX') or v.get('mapx')
                sub_hy = v.get('y') or v.get('mapY') or v.get('mapy')
                if sub_hx is not None and sub_hy is not None:
                    try:
                        sub_hid = v.get('id') or v.get('primaryKey') or k
                        key = f"{int(sub_hx)}_{int(sub_hy)}"
                        if key in known_map:
                            known_map[key]['id_habitat'] = sub_hid
                            found_set.add(key)
                    except: pass
            extract_hidden_ids(v, known_map, found_set)
            
    elif isinstance(node, list):
        for item in node:
            extract_hidden_ids(item, known_map, found_set)

def enrich_with_habitat_ids(client, temp_map, castelli_senza_id):
    """Arricchimento ID Mirato"""
    print("🔑 Avvio recupero HabitatID via MapAction (Modalità Mirata)...")
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
    
    zone_da_scaricare = set()
    for entry in castelli_senza_id.values():
        zone_da_scaricare.add((entry['x'] // 32, entry['y'] // 32))
    
    print(f"🗺️ Zone da interrogare per i nuovi ID: {len(zone_da_scaricare)}")
    habitat_trovati = 0
    
    for tx, ty in zone_da_scaricare:
        url = f"{BACKEND_URL}/XYRALITY/WebObjects/{SERVER_ID}.woa/wa/MapAction/map"
        payload = {
            'mapX': str(tx*32), 'mapY': str(ty*32), 
            'mapWidth': '32', 'mapHeight': '32', 
            'worldId': WORLD_ID, 'logoutUrl': 'http://lordsandknights.com/'
        }
        try:
            time.sleep(random.uniform(1.5, 3.5)) 
            res = session.post(url, data=payload, timeout=15)
            if res.status_code == 200:
                data = plistlib.loads(res.content)
                found_in_this_request = set()
                extract_hidden_ids(data, temp_map, found_in_this_request)
                habitat_trovati += len(found_in_this_request)
        except Exception: continue

    print(f"🎯 Finito! Aggiunti {habitat_trovati} nuovi HabitatID nel database.")

def enrich_db_with_names(db, player_map, alliance_map):
    count_updated = 0
    for key, record in db.items():
        pid = record.get('p')
        if pid and pid != 0:
            nome_nuovo = player_map.get(pid, "Sconosciuto")
            if 'pn' not in record or record['pn'] == "Sconosciuto" or (record['pn'] != nome_nuovo and nome_nuovo != "Sconosciuto"):
                 record['pn'] = nome_nuovo
                 count_updated += 1
                 
        aid = record.get('a')
        if aid and aid != 0:
            nome_alleanza = alliance_map.get(aid, "")
            if 'an' not in record or record['an'] == "" or (record['an'] != nome_alleanza and nome_alleanza != ""):
                 record['an'] = nome_alleanza
                 
    print(f"♻️ Nomi e Alleanze aggiornati per {count_updated} castelli nel database.")
    return db

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
    print("🚀 FASE 1: INIZIALIZZAZIONE")
    if not os.path.exists(FILE_DATABASE):
        with open(FILE_DATABASE, 'w') as f: json.dump([], f)
        
    temp_map = {}
    with open(FILE_DATABASE, 'r') as f:
        for entry in json.load(f): temp_map[f"{entry['x']}_{entry['y']}"] = entry
        
    old_db_list = copy.deepcopy(list(temp_map.values()))
    print(f"📂 Database caricato: {len(temp_map)} castelli.")

    print("\n🌍 FASE 2: SCANSIONE MAPPA PUBBLICA (Senza Login)")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    })
    
    punti_caldi = {}
    for entry in temp_map.values():
        tx, ty = entry['x'] // 32, entry['y'] // 32
        punti_caldi[f"{tx}_{ty}"] = (tx, ty)

    for tx, ty in punti_caldi.values():
        process_tile_public(tx, ty, session, temp_map)

    centerX, centerY = 256, 256
    if temp_map:
        vals = list(temp_map.values())
        if vals:
            centerX = sum(e['x']//32 for e in vals) // len(vals)
            centerY = sum(e['y']//32 for e in vals) // len(vals)

    vuoti = 0
    for r in range(1, 150):
        trovato = False
        xMin, xMax = centerX - r, centerX + r
        yMin, yMax = centerY - r, centerY + r
        punti = []
        
        for i in range(xMin, xMax + 1): 
            if 0 <= i <= 600:
                if 0 <= yMin <= 600: punti.append((i, yMin))
                if 0 <= yMax <= 600: punti.append((i, yMax))
        for j in range(yMin + 1, yMax): 
            if 0 <= j <= 600:
                if 0 <= xMin <= 600: punti.append((xMin, j))
                if 0 <= xMax <= 600: punti.append((xMax, j))
        
        punti = list(set(punti))
        
        for px, py in punti:
            if f"{px}_{py}" not in punti_caldi:
                if process_tile_public(px, py, session, temp_map): 
                    trovato = True
                punti_caldi[f"{px}_{py}"] = (px, py)
        
        if trovato: 
            vuoti = 0
        else: 
            vuoti += 1
            
        if vuoti >= 10: 
            print(f"🛑 Raggiunto limite di spazi vuoti (Raggio: {r}). Fine mappa rilevata.")
            break

    print("\n🔐 FASE 3: ACCESSO GIOCO E ARRICCHIMENTO DATI")
    EMAIL = os.getenv("LK_EMAIL")
    PASSWORD = os.getenv("LK_PASSWORD")
    
    client = None
    if EMAIL and PASSWORD:
        client = RePanzaClient.auto_login(EMAIL, PASSWORD)
    
    if client:
        # Recupera nomi e alleanze
        player_map = fetch_ranking(client)
        alliance_map = fetch_alliance_ranking(client)
        
        # Inserisce i nomi nel database grezzo
        temp_map = enrich_db_with_names(temp_map, player_map, alliance_map)
        
        # Controlla ID Habitat mancanti
        castelli_senza_id = {k: v for k, v in temp_map.items() if 'id_habitat' not in v}
        if not castelli_senza_id:
            print("⚡ Nessun nuovo castello rilevato. Salto estrazione HabitatID.")
        else:
            print(f"⚠️ Rilevati {len(castelli_senza_id)} nuovi castelli senza ID.")
            enrich_with_habitat_ids(client, temp_map, castelli_senza_id)
    else:
        print("❌ Login fallito. Impossibile scaricare nomi e nuovi ID Habitat.")
        send_telegram_alert(WORLD_NAME)

    print("\n💾 FASE 4: SALVATAGGIO FINALE E CRONOLOGIA")
    temp_map = run_inactivity_check(temp_map)
    new_db_list = list(temp_map.values())
    run_history_check(old_db_list, new_db_list, FILE_HISTORY)
    
    final_list = [v for v in temp_map.values() if v['d'] > (time.time() - 259200)]
    
    with open(FILE_DATABASE, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Operazione conclusa con successo! {len(final_list)} record salvati.")

if __name__ == "__main__":
    run_unified_scanner()
