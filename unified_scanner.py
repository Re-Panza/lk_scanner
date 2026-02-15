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
    messaggio = f"Capo, il login per '{world_name}' è fallito. Scansione pubblica avviata comunque."
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try: requests.post(url, json={"chat_id": chat_id, "text": messaggio})
    except: pass

class RePanzaClient:
    def __init__(self, cookies, user_agent):
        self.cookies = cookies
        self.user_agent = user_agent

    @staticmethod
    def auto_login(email, password):
        with sync_playwright() as p:
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            args = ['--disable-blink-features=AutomationControlled', '--no-sandbox']
            browser = p.chromium.launch(headless=True, args=args)
            context = browser.new_context(user_agent=ua)
            page = context.new_page()
            try:
                page.goto("https://www.lordsandknights.com/", timeout=60000)
                time.sleep(random.uniform(2, 4))
                page.type('input[placeholder="Email"]', email, delay=100)
                page.type('input[placeholder="Password"]', password, delay=100)
                page.click('button:has-text("LOG IN")')
                
                selector_mondo = page.locator(f".button-game-world--title:has-text('{WORLD_NAME}')").first
                start_time = time.time()
                while time.time() - start_time < 300:
                    if selector_mondo.is_visible():
                        selector_mondo.click(force=True)
                    cookies = context.cookies()
                    if any(c['name'] == 'sessionID' for c in cookies):
                        final_cookies = context.cookies()
                        browser.close()
                        return RePanzaClient(final_cookies, ua)
                    time.sleep(2)
            except: pass
            browser.close()
            return None

def fetch_ranking(client):
    session = requests.Session()
    for cookie in client.cookies: session.cookies.set(cookie['name'], cookie['value'])
    url = f"{BACKEND_URL}/XYRALITY/WebObjects/{SERVER_ID}.woa/wa/QueryAction/playerRanks"
    all_players = {}
    offset = 0
    while True:
        payload = {'offset': str(offset), 'limit': '100', 'type': '(player_rank)', 'worldId': WORLD_ID}
        try:
            res = session.post(url, data=payload, timeout=20)
            data = plistlib.loads(res.content)
            players = data.get('playerRanks', [])
            if not players: break
            for p in players: all_players[int(p['playerID'])] = p['nick']
            offset += 100
            time.sleep(random.uniform(0.5, 1))
        except: break
    return all_players

def process_tile_public(x, y, session, tmp_map, player_map):
    """Scansione JTILE Pubblica (Senza Login)"""
    url = f"{BACKEND_URL}/maps/{SERVER_ID}/{x}_{y}.jtile"
    try:
        time.sleep(random.uniform(0.1, 0.3))
        response = session.get(url, timeout=10)
        if response.status_code != 200: return False
        match = re.search(r'\((.*)\)', response.text, re.S)
        if match:
            data = json.loads(match.group(1))
            if 'habitatArray' in data:
                for h in data['habitatArray']:
                    pid = int(h['playerid'])
                    key = f"{h['mapx']}_{h['mapy']}"
                    tmp_map[key] = {
                        'p': pid, 'pn': player_map.get(pid, "Sconosciuto"),
                        'a': int(h['allianceid']), 'n': h.get('name', ''),
                        'x': int(h['mapx']), 'y': int(h['mapy']),
                        'pt': int(h['points']), 't': int(h['habitattype']),
                        'd': int(time.time())
                    }
                return True
    except: pass
    return False

def enrich_with_habitat_ids(client, temp_map):
    """Arricchimento ID tramite MapAction (Richiede Login)"""
    print("🔑 Tentativo di recupero HabitatID via MapAction...")
    session = requests.Session()
    for cookie in client.cookies: session.cookies.set(cookie['name'], cookie['value'])
    
    # Raggruppiamo i castelli per zone 32x32 per minimizzare le richieste
    zone_da_scaricare = set()
    for entry in temp_map.values():
        zone_da_scaricare.add((entry['x'] // 32, entry['y'] // 32))
    
    for tx, ty in zone_da_scaricare:
        url = f"{BACKEND_URL}/XYRALITY/WebObjects/{SERVER_ID}.woa/wa/MapAction/map"
        payload = {'mapX': str(tx*32), 'mapY': str(ty*32), 'mapWidth': '32', 'mapHeight': '32', 'worldId': WORLD_ID}
        try:
            time.sleep(random.uniform(1.5, 3.5)) # Simulazione umana
            res = session.post(url, data=payload, timeout=15)
            if res.status_code == 200:
                data = plistlib.loads(res.content)
                for h in data.get('h', []):
                    key = f"{h['x']}_{h['y']}"
                    if key in temp_map:
                        temp_map[key]['id_habitat'] = h['id']
        except: continue

def run_unified_scanner():
    EMAIL = os.getenv("LK_EMAIL")
    PASSWORD = os.getenv("LK_PASSWORD")
    client = RePanzaClient.auto_login(EMAIL, PASSWORD) if EMAIL and PASSWORD else None
    
    player_map = fetch_ranking(client) if client else {}
    if not client: send_telegram_alert(WORLD_NAME)

    temp_map = {}
    if os.path.exists(FILE_DATABASE):
        with open(FILE_DATABASE, 'r') as f:
            for entry in json.load(f): temp_map[f"{entry['x']}_{entry['y']}"] = entry

    session = requests.Session()
    print("🛰️ Avvio Scansione JTILE Pubblica...")
    # Qui inserisci la tua logica a spirale esistente che chiama process_tile_public
    # [Logica spirale omessa per brevità, usa quella del tuo file originale]

    if client:
        enrich_with_habitat_ids(client, temp_map)

    final_list = list(temp_map.values())
    with open(FILE_DATABASE, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
    print(f"✅ Scansione Completata. Database salvato con {len(final_list)} record.")

if __name__ == "__main__":
    run_unified_scanner()
