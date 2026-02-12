import os
import json
import requests
import time
import plistlib
import re
from playwright.sync_api import sync_playwright

# --- CONFIGURAZIONE ---
SERVER_ID = "LKWorldServer-RE-IT-6"
WORLD_ID = "327"  # ID del mondo (Se è sbagliato, la lista giocatori sarà vuota)
BACKEND_URL = "https://backend3.lordsandknights.com"
FILE_DATABASE = "database_mondo_327.json"
FILE_HISTORY = "cronologia_327.json"

# --- 1. Rilevatore Dispositivo & Utility ---

class RePanzaClient:
    def __init__(self, session_id, cookies, user_agent):
        self.session_id = session_id
        self.cookies = cookies
        self.user_agent = user_agent

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            
            # Parametri anti-rilevamento
            args = [
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars',
                '--window-position=0,0',
                '--ignore-certificate-errors',
            ]

            browser = p.chromium.launch(headless=True, args=args)
            context = browser.new_context(viewport={'width': 1366, 'height': 768}, user_agent=ua)
            page = context.new_page()
            
            # Nasconde il fatto che è un bot
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            capture = {"sid": None}

            def intercept_response(response):
                if "login" in response.url and response.status == 200:
                    try:
                        cookies = context.cookies()
                        for c in cookies:
                            if c['name'] == 'sessionID':
                                capture["sid"] = c['value']
                    except: pass

            page.on("response", intercept_response)
            
            try:
                print("🌐 Caricamento Lords & Knights...")
                page.goto("https://www.lordsandknights.com/", wait_until="domcontentloaded", timeout=60000)
                
                # Attesa dinamica dei campi
                try:
                    page.wait_for_selector('input[placeholder="Email"]', state="visible", timeout=20000)
                except Exception as e:
                    print("⚠️ Campi login non trovati. Scatto foto debug_login_missing.png")
                    page.screenshot(path="debug_login_missing.png")
                    raise e

                print("✍️ Inserimento credenziali...")
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
                    
                    if capture["sid"]:
                        all_cookies = context.cookies()
                        sid_final = capture["sid"]
                        print(f"✅ Login Successo!")
                        browser.close()
                        return RePanzaClient(sid_final, all_cookies, ua)
                    time.sleep(1)
                
                print("❌ Timeout selezione mondo. Screenshot debug_timeout_world.png")
                page.screenshot(path="debug_timeout_world.png")

            except Exception as e:
                print(f"⚠️ Errore Login Critico: {e}")
                try:
                    page.screenshot(path="debug_crash.png")
                except: pass
            
            browser.close()
            return None

def fetch_ranking(client):
    session = requests.Session()
    for cookie in client.cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    session.headers.update({
        'User-Agent': client.user_agent,
        'Accept': 'application/x-bplist',
        'Content-Type': 'application/x-www-form-urlencoded'
    })

    url_ranking = f"{BACKEND_URL}/XYRALITY/WebObjects/{SERVER_ID}.woa/wa/QueryAction/playerRanks"
    all_players = {}
    offset = 0
    step = 100
    
    print(f"🚀 Recupero Classifica (Mondo ID: {WORLD_ID})...")
    
    # --- BLOCCO DEBUG DIAGNOSTICO ---
    # Esegue una richiesta di prova e stampa la risposta grezza per capire l'errore
    try:
        print("🔍 [DEBUG] Invio richiesta test al server...")
        debug_payload = {
            'offset': '0', 
            'limit': '10', 
            'type': '(player_rank)', 
            'sortBy': '(row.asc)', 
            'worldId': WORLD_ID
        }
        debug_resp = session.post(url_ranking, data=debug_payload, timeout=30)
        print(f"🔍 [DEBUG] Status Code: {debug_resp.status_code}")
        
        # Stampa i primi 300 caratteri della risposta per vedere se è un errore leggibile
        raw_text = debug_resp.text[:300].replace('\n', ' ') 
        print(f"📄 [DEBUG] Risposta Raw: {raw_text}")
        
        try:
            debug_data = plistlib.loads(debug_resp.content)
            print(f"📦 [DEBUG] Chiavi nel PLIST: {list(debug_data.keys())}")
            if 'error' in debug_data:
                print(f"⚠️ [DEBUG] ERRORE DAL SERVER: {debug_data['error']}")
            if 'playerRanks' in debug_data and len(debug_data['playerRanks']) == 0:
                print(f"⚠️ [DEBUG] La lista 'playerRanks' è vuota. ID Mondo {WORLD_ID} potrebbe essere errato.")
        except Exception as e:
            print(f"⚠️ [DEBUG] Impossibile decodificare PLIST: {e}")
    except Exception as e:
        print(f"💥 [DEBUG] Errore connessione test: {e}")
    # ---------------------------------

    while True:
        try:
            payload = {'offset': str(offset), 'limit': str(step), 'type': '(player_rank)', 'sortBy': '(row.asc)', 'worldId': WORLD_ID}
            response = session.post(url_ranking, data=payload, timeout=30)
            if response.status_code != 200: break
            
            data = plistlib.loads(response.content)
            players = data.get('playerRanks', []) or data.get('rows', [])
            
            if not players: break
            
            for p in players:
                pid = p.get('playerID') or p.get('p')
                name = p.get('nick') or p.get('n')
                if pid: all_players[int(pid)] = name
            
            if len(players) < step: break
            offset += step
            time.sleep(0.2)
        except Exception as e:
            print(f"💥 Errore durante il loop classifica: {e}")
            break
    
    print(f"✅ Mappati {len(all_players)} giocatori.")
    return all_players

def process_tile(x, y, session, tmp_map, player_map):
    url = f"{BACKEND_URL}/maps/{SERVER_ID}/{x}_{y}.jtile"
    try:
        response = session.get(url, timeout=10)
        if response.status_code != 200: return False
        content = response.text
        if "callback_politicalmap({})" in content: return False
        
        match = re.search(r'\((.*)\)', content, re.S)
        if match:
            data = json.loads(match.group(1))
            if 'habitatArray' in data:
                for h in data['habitatArray']:
                    pid = int(h['playerid'])
                    key = f"{h['mapx']}_{h['mapy']}"
                    
                    # Nome giocatore: se non c'è nella mappa globale, usa "Sconosciuto"
                    player_name = player_map.get(pid, "Sconosciuto")
                    
                    tmp_map[key] = {
                        'p': pid,
                        'pn': player_name,
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
    # Correzione per errore TypeError (int vs str)
    now = time.time()
    for key, h in data.items():
        if not h.get('p') or h['p'] == 0: continue
        
        firma_attuale = f"{h['n']}|{h['pt']}"
        h['d'] = int(h['d'])
        
        if 'u' not in h:
            h['u'] = h['d']
            h['i'] = False
            h['f'] = firma_attuale
            continue
            
        try:
            last_update = int(h['u'])
        except (ValueError, TypeError):
            last_update = h['d']
            h['u'] = h['d']

        if h.get('f') != firma_attuale:
            h['u'] = h['d']
            h['i'] = False
            h['f'] = firma_attuale
        else:
            if (h['d'] - last_update) >= 86400:
                h['i'] = True
    return data

def run_history_check(old_data, current_player_map, current_map, history_file):
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except: pass

    last_known = {}
    for h in old_data:
        pid = h.get('p')
        if pid:
            if pid not in last_known:
                last_known[pid] = {'n': h.get('pn'), 'a': h.get('a')}

    now = int(time.time())
    new_events = []

    # 1. Cambi nome
    for pid, current_name in current_player_map.items():
        if pid in last_known:
            old_name = last_known[pid]['n']
            if old_name and old_name != "Sconosciuto" and old_name != current_name:
                new_events.append({"p": pid, "pn": current_name, "type": "name_change", "old": old_name, "new": current_name, "d": now})

    # 2. Cambi alleanza
    current_alliances = {}
    for h in current_map.values():
        pid = h.get('p')
        if pid: current_alliances[pid] = h.get('a')

    for pid, current_aid in current_alliances.items():
        if pid in last_known:
            old_aid = last_known[pid]['a']
            if old_aid is not None and old_aid != current_aid:
                new_events.append({"p": pid, "pn": current_player_map.get(pid, "Sconosciuto"), "type": "alliance_change", "old": old_aid, "new": current_aid, "d": now})

    if new_events:
        history.extend(new_events)
        if len(history) > 1000: history = history[-1000:]
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"✅ Aggiunti {len(new_events)} eventi in cronologia.")

def run_unified_scanner():
    # --- FIX FILES ---
    # Crea file se non esistono per evitare errori git
    if not os.path.exists(FILE_DATABASE):
        with open(FILE_DATABASE, 'w') as f: json.dump([], f)
    if not os.path.exists(FILE_HISTORY):
        with open(FILE_HISTORY, 'w') as f: json.dump([], f)

    EMAIL = os.getenv("LK_EMAIL")
    PASSWORD = os.getenv("LK_PASSWORD")
    
    player_map = {}
    if EMAIL and PASSWORD:
        client = RePanzaClient.auto_login(EMAIL, PASSWORD)
        if client: 
            player_map = fetch_ranking(client)
        else: 
            print("⚠️ Login fallito. Procedo senza nomi aggiornati.")
    else:
        print("❌ Credenziali mancanti. Procedo in modalità anonima.")

    # Carica DB
    temp_map = {}
    old_data_list = []
    if os.path.exists(FILE_DATABASE):
        try:
            with open(FILE_DATABASE, 'r', encoding='utf-8') as f:
                old_data_list = json.load(f)
                for entry in old_data_list:
                    temp_map[f"{entry['x']}_{entry['y']}"] = entry
        except: pass

    # Scansione
    print(f"🛰️ Avvio Scansione Mappa (Database attuale: {len(temp_map)} castelli)...")
    session = requests.Session()
    punti_caldi = {}
    for entry in temp_map.values():
        tx, ty = entry['x'] // 32, entry['y'] // 32
        punti_caldi[f"{tx}_{ty}"] = (tx, ty)

    for tx, ty in punti_caldi.values():
        process_tile(tx, ty, session, temp_map, player_map)

    # Espansione Intelligente
    centerX, centerY = 503, 503
    if temp_map:
        try:
            vals = list(temp_map.values())
            if vals:
                centerX = sum(e['x']//32 for e in vals) // len(vals)
                centerY = sum(e['y']//32 for e in vals) // len(vals)
        except: pass

    raggioMax = 150 
    limiteVuoti = 5
    vuoti_consecutivi = 0
    
    for r in range(raggioMax + 1):
        trovato = False
        xMin, xMax = centerX - r, centerX + r
        yMin, yMax = centerY - r, centerY + r
        punti_perimetro = []
        for i in range(xMin, xMax + 1):
            punti_perimetro.append((i, yMin)); punti_perimetro.append((i, yMax))
        for j in range(yMin + 1, yMax):
            punti_perimetro.append((xMin, j)); punti_perimetro.append((xMax, j))
            
        for px, py in punti_perimetro:
            key = f"{px}_{py}"
            if key not in punti_caldi:
                if process_tile(px, py, session, temp_map, player_map): trovato = True
                punti_caldi[key] = (px, py)
        
        if trovato: vuoti_consecutivi = 0
        else: vuoti_consecutivi += 1
        if vuoti_consecutivi >= limiteVuoti: break

    # Analisi Inattività e Storico
    print("🧹 Analisi inattività...")
    temp_map = run_inactivity_check(temp_map)
    
    print("📜 Aggiornamento cronologia...")
    run_history_check(old_data_list, player_map, temp_map, FILE_HISTORY)
    
    limite = time.time() - (72 * 3600)
    final_list = [v for v in temp_map.values() if v['d'] > limite]

    # Salvataggio
    print(f"💾 Salvataggio DB ({len(final_list)} record)...")
    with open(FILE_DATABASE, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Scansione Completata.")

if __name__ == "__main__":
    run_unified_scanner()
