import asyncio
import websockets, socket, time, urllib.request, json, requests
import threading
from discordrp import Presence
from websockets.legacy.server import WebSocketServerProtocol as wetSocks
import re
import os
from xml.etree import ElementTree as ET
import urllib.parse
import html
import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.error import HTTPError, URLError
import configparser

config = configparser.ConfigParser()
config.read("config.cfg")

clientID = config.get("discord", "clientID")
presence = Presence(str(clientID))

# Load API keys from config
TMDB_API_KEY = config.get("keys", "tmdb_api_key")
TVDB_API_KEY = config.get("keys", "tvdb_api_key")
YOUTUBE_API = config.get("keys", "youtube_api")
SPOTIFY_API = config.get("keys", "spotify_api")
XLINK_API = config.get("keys", "xlink_api")

# Load PS3/360 addresses and scan intervals from config
PS3_ADDRESS = config.get("network", "PS3_ADDRESS")
X360_ADDRESS = config.get("network", "X360_ADDRESS")
SCAN_INTERVAL = config.getint("network", "SCAN_INTERVAL")

# Load IDs from config
insignia_id = config.get("profiles", "insignia_id")
xtag = config.get("profiles", "xtag")
gamertag = config.get("profiles", "gamertag")
playstation_id = config.get("profiles", "playstation_id")
rpcn_id = config.get("profiles", "rpcn_id")
wiimmfi_id = config.get("profiles", "wiimmfi_id")
pretendo_id = config.get("profiles", "pretendo_id")
nintendo_id = config.get("profiles", "nintendo_id")

# Xbox + 360 API + CDN
XBOX_APIURL = "https://mobcat.zip/XboxIDs"
XBOX_CDNURL = "https://raw.githubusercontent.com/MobCat/MobCats-original-xbox-game-list/main/icon"
XBOX_HOMEBREW_CDNURL = "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/images/xbox/homebrew"
X360_CDNURL = "https://raw.githubusercontent.com/MobCat/MobCats-xbox-360-game-list/main/icon"
X360_HOMEBREW_CDNURL = "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/images/360/homebrew"
XONE_CDNURL = ""
XONE_HOMEBREW_CDNURL = ""

# Nintendo API + CDN (GameTDB)
GC_CDNURL = "https://art.gametdb.com/wii/cover/"
WII_CDNURL = "https://art.gametdb.com/wii/cover/"
SWITCH_CDNURL = "https://art.gametdb.com/switch/cover/"
DS_CDNURL = "https://art.gametdb.com/ds/cover/"
N3DS_CDNURL = "https://art.gametdb.com/3ds/cover/"
WIIU_CDNURL = "https://art.gametdb.com/wiiu/cover/"


# Sony API + CDN
PS1_CDNURL = "https://raw.githubusercontent.com/xlenore/psx-covers/refs/heads/main/covers/default"
PS2_CDNURL = "https://raw.githubusercontent.com/xlenore/ps2-covers/refs/heads/main/covers/default"
PS3_CDNURL = "https://raw.githubusercontent.com/aldostools/resources/master/COV"
PS4_CDNURL = "https://raw.githubusercontent.com/aldostools/resources/master/COV"
PS5_CDNURL = "https://raw.githubusercontent.com/aldostools/resources/master/COV"
PSP_CDNURL = "https://raw.githubusercontent.com/andiweli/hexflow-covers/refs/heads/main/Covers/PSP"
VITA_CDNURL = "https://raw.githubusercontent.com/andiweli/hexflow-covers/refs/heads/main/Covers/PSVita"

# Sega API + CDN
DC_CDN = "https://raw.githubusercontent.com/faithvoid/dc-covers/main/serial"

# Generic icons
MUSIC_LARGE = "https://cdn.discordapp.com/app-assets/1379734520508579960/1380359849233092659.png"
VIDEO_LARGE = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393415855273935009.png"
MUSIC_SMALL = "https://cdn.discordapp.com/app-assets/1379734520508579960/1379736461946916874.png"

# Dashboard Logos
XBMC_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1379735600613167104.png"
THESEUS_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393133351099174943.png"
UIX_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393133351099174943.png"
CORTANAOS_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393481542910611476.png"
XBMC4GAMERS_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1379735600613167104.png"
XBMCEMUSTATION_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1379735600613167104.png"
AVALAUNCH_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393054192956084427.png"
UNLEASHX_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393053976789778515.png"

# Console Logos
XBOX_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393133351099174943.png"
X360_LOGO = "https://raw.githubusercontent.com/OfficialTeamUIX/Xbox-Discord-Rich-Presence/main/xbdStats-resources/xbox360.png"
XONE_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1395349111842017350.png"
DS_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1395327411662487632.png"
N3DS_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1395327527509033072.png"
PSP_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393346915395043530.png"
VITA_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1394468854947909705.png"
PS2_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393349505382088864.png"
PS3_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393346911406395506.png"
PS4_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1395258501001117726.png"
PS5_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1395326377539928165.png"
PS1_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393346910924050523.png"
DC_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393203893789392989.png"
GC_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393326642847285328.png"
WII_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393309017333432370.png"
WIIU_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1393332654618968184.png"
SWITCH_LOGO = "https://cdn.discordapp.com/app-assets/1379734520508579960/1395508580064694364.png"

# API Keys
_tvdb_jwt = None
_tvdb_jwt_time = 0

# Music button sources, toggle True/False depending on what you want to display. You can only have two at a time.
YouTube = True
Spotify = True
Discogs = True

# Game button sources, toggle True/False depending on what you want to display. You can only have two at a time.
Insignia = True
XLinkKai = True
Wikipedia = True
eBay = True
MobCat = True

# Video button sources, toggle True/False depending on what you want to display. You can only have two at a time.
IMDB = True
TVDB = True
Netflix = True

# Global title dictionaries
titles = {
    "xbox": {},
    "xbox360": {},
    "xboxone": {},
    "ps1": {},
    "ps2": {},
    "ps3": {},
    "ps4": {},
    "psp": {},
    "vita": {},
    "ds": {},
    "3ds": {},
    "gc-wii": {},
    "wiiu": {},
    "switch": {},
    "dc": {},
}

md5 = {
    "xbox": {},
    "360": {},
    "switch": {},
    "psp": {},
    "vita": {},
}

def load_titles(name, path=None, is_url=False, fmt='txt', delimiter=None, index_map=(0, 1), json_key_map=None):
    try:
        if fmt == 'json':
            if is_url:
                with urllib.request.urlopen(path) as response:
                    data = json.load(response)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

            if json_key_map:
                for entry in data:
                    tid = entry.get(json_key_map[0], "").upper()
                    title = entry.get(json_key_map[1], "")
                    if tid and title:
                        titles[name][tid] = title
            else:
                # Handles dictionary-style JSON
                titles[name] = data

            print(f"[{name.upper()}] Loaded {len(titles[name])} titles from {path}")
            return

        # Default non-JSON loading below
        data_lines = []

        if is_url:
            with urllib.request.urlopen(path) as response:
                data_lines = [line.decode('utf-8', errors='replace').strip() for line in response]
        else:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                data_lines = [line.strip() for line in f]

        for line in data_lines:
            if not line:
                continue
            if delimiter:
                parts = line.split(delimiter)
            else:
                parts = line.split(maxsplit=1)

            if len(parts) <= max(index_map):
                continue
            tid = parts[index_map[0]].strip("'").strip().upper()
            title = parts[index_map[1]].strip()
            titles[name][tid] = title

        print(f"[{name.upper()}] Loaded {len(titles[name])} titles from {path}")
    except Exception as e:
        print(f"[{name.upper()}] Failed to load titles from {path or 'URL'}: {e}")

# Load MD5 checksums for homebrew applications, as their titleIDs are usually invalid.
def load_md5(name, path=None, is_url=False, fmt='txt', delimiter=None, index_map=(0, 1), json_key_map=None):
    try:
        if fmt == 'json':
            if is_url:
                with urllib.request.urlopen(path) as response:
                    data = json.load(response)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

            if json_key_map:
                for entry in data:
                    tid = entry.get(json_key_map[0], "").upper()
                    title = entry.get(json_key_map[1], "")
                    if tid and title:
                        md5[name][tid] = title
            else:
                # Handles dictionary-style JSON
                md5[name] = data

            print(f"[{name.upper()}] Loaded {len(titles[name])} titles from {path}")
            return

        # Default non-JSON loading below
        data_lines = []

        if is_url:
            with urllib.request.urlopen(path) as response:
                data_lines = [line.decode('utf-8', errors='ignore').strip() for line in response]
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data_lines = [line.strip() for line in f]

        for line in data_lines:
            if not line:
                continue
            if delimiter:
                parts = line.split(delimiter)
            else:
                parts = line.split(maxsplit=1)

            if len(parts) <= max(index_map):
                continue
            tid = parts[index_map[0]].strip("'").strip().upper()
            title = parts[index_map[1]].strip()
            titles[name][tid] = title

        print(f"[{name.upper()}] Loaded {len(titles[name])} titles from {path}")
    except Exception as e:
        print(f"[{name.upper()}] Failed to load titles from {path or 'URL'}: {e}")

# Sony
load_titles("ps1", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/ps1.txt", is_url=True)
load_titles("ps2", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/ps2.txt", is_url=True, delimiter=',', index_map=(0, 2))
load_titles("ps3", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/ps3.txt", is_url=True)
load_titles("ps4", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/ps4.txt", is_url=True)
load_titles("psp", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/psp.txt", is_url=True)
load_titles("psp", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/homebrew/psp.txt", is_url=True) # Homebrew
load_md5("psp", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/homebrew/psp_md5.txt", is_url=True) # Homebrew (MD5)
load_titles("vita", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/vita.txt", is_url=True)
load_titles("vita", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/homebrew/vita.txt", is_url=True) # Homebrew
load_md5("vita", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/homebrew/vita_md5.txt", is_url=True) # Homebrew (MD5)
# Nintendo
load_titles("gc-wii", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/gc-wii.txt", is_url=True)
load_titles("wiiu", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/wiiu.txt", is_url=True)
load_titles("ds", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/ds.txt", is_url=True)
load_titles("3ds", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/3ds.txt", is_url=True)
load_titles("switch", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/switch.txt", is_url=True)
load_md5("switch", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/homebrew/switch.txt", is_url=True) # Homebrew
load_md5("switch", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/homebrew/switch_md5.txt", is_url=True) # Homebrew (MD5)
# Sega
load_titles("dc", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/dc.txt", is_url=True)
# Microsoft
load_titles("xbox", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/homebrew/xbox.txt", is_url=True)
load_md5("xbox", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/homebrew/xbox_md5.txt", is_url=True)
load_titles("xbox360", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/xbox360.txt", is_url=True)
load_titles("xbox360", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/homebrew/360.txt", is_url=True) # Homebrew
load_md5("xbox360", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/homebrew/360_md5.txt", is_url=True) # Homebrew (MD5)
load_titles("xboxone", "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/titles/xboxone.txt", is_url=True)

def get_ps3_status(ps3_ip):
    ps3_url = f"http://{PS3_ADDRESS}/cpursx.ps3"
    try:
        with urllib.request.urlopen(ps3_url, timeout=15) as response:
            webman = urllib.request.urlopen(ps3_url).read()
            soup = BeautifulSoup(webman, 'html.parser')
            atags = soup.find_all('a')
            
            ps3_id = "PS3_DASHBOARD"
            temp = []
            
            for tag in atags:
                temp.append(tag.get_text())
                if len(temp) > 18:
                    ps3_id = temp[18]
                else:
                    ps3_id = "PS3_DASHBOARD"
            if len(ps3_id) < 10 and ":" not in ps3_id:
                return ps3_id
            else:
                return "PS3_DASHBOARD"

    except (HTTPError, URLError, TimeoutError) as error:
        print(error)

def poll_ps3_webman(ip, interval=60):
    last_tid = 0
    while True:
        tid = get_ps3_status(ip)
        if tid:
            tid = tid.upper()
            if tid != last_tid:
                last_tid = tid
                if tid == "PS3_DASHBOARD":
                    set_presence(tid, "XMB", "DASHBOARD", True, False)
                    logging.info("[PS3] Now in Dashboard (XMB)")
                else:
                    title = titles["ps3"].get(tid, "Unknown Title")
                    set_presence(tid, title, "PS3", True, False)
                    logging.info(f"[PS3] Now Playing {tid} - {title}")
            elif tid == last_tid:
                logging.info(f"[PS3] No change ({tid})")
        else:
            logging.warning("[PS3] Could not connect to WebMAN")
        
        time.sleep(interval)

def get_ps3_title_id(ip, port=80, timeout=3):
    try:
        # Make HTTP request to Webman API
        response = requests.get(f"http://{ip}/cpursx.ps3", timeout=timeout)
        if response.status_code == 200:
            # Parse the response to extract game title
            content = response.text
            # Example format: "Game: [BLUS12345] Some Game Title"
            match = re.search(r"Game:\s*\[([A-Z0-9]+)\]\s*(.*)", content)
            if match:
                tid = match.group(1).upper()
                title = match.group(2).strip()
                return tid, title  # Return both ID and title
    except Exception as e:
        logging.warning(f"[PS3] Failed to retrieve Title ID via Webman: {e}")
    return None, None

def set_presence(tid, title, platform, *_):
    if platform == "PS3":
        dataIn = {"ps3": True, "id": tid, "name": title}
    elif platform == "XBOX360":
        dataIn = {"xbox360": True, "id": tid, "name": title}
    elif platform == "DASHBOARD":
        dataIn = {"dashboard": True, "id": tid, "name": title}
    else:
        return
    build_presence(dataIn)


# Broadcast "XBDSTATS_ONLINE" for auto-discovery
def broadcast_online(port=1102, interval=3):
    bc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    msg = b"XBDSTATS_ONLINE"
    while True:
        try:
            bc_sock.sendto(msg, ('<broadcast>', port))
        except Exception as e:
            print("[Broadcast] Error:", e)
        time.sleep(interval)

# Get token from TVDB
def get_tvdb_jwt():
    global _tvdb_jwt, _tvdb_jwt_time
    if _tvdb_jwt and (time.time() - _tvdb_jwt_time) < 14400:
        return _tvdb_jwt
    url = 'https://api4.thetvdb.com/v4/login'
    data = json.dumps({"apikey": TVDB_API_KEY}).encode("utf-8")
    resp = requests.post(url, data=data, headers={'Content-Type': 'application/json'}, timeout=5)
    resp.raise_for_status()
    _tvdb_jwt = resp.json()['data']['token']
    _tvdb_jwt_time = time.time()
    return _tvdb_jwt

# Normalize text
def normalize(text):
    text = html.unescape(text)  # Decode HTML entities
    text = re.sub(r'[^a-z0-9 ]', '', text.lower())  # Remove punctuation but keep spaces
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    return text.strip()

# Splits artist title information for MusicBrainz usage
def split_artist_title(idstr):
    # Accepts "Artist - Title" and splits it
    parts = idstr.split(' - ', 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, None

# Fetch various information (ie; cover art) for music files via MusicBrainz  
def fetch_musicbrainz_info(artist, title):
    try:
        # Search recording by artist and title
        query = f'artist:"{artist}" AND recording:"{title}"'
        url = f'https://musicbrainz.org/ws/2/recording/?query={urllib.parse.quote(query)}&fmt=json&limit=1'
        headers = {'User-Agent': 'sakuraPresence/1.0 ( contact: faithvoid@github or https://github.com/faithvoid )'}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        results = resp.json().get('recordings', [])
        if not results:
            return None, None, None, None, None

        rec = results[0]
        track_title = rec.get('title', title)
        artist_name = rec['artist-credit'][0]['name'] if rec.get('artist-credit') else artist

        release_list = rec.get('releases', [])
        album_title = release_date = None
        release_mbid = None

        if release_list:
            release = release_list[0]
            album_title = release.get('title')
            release_date = release.get('date', None)
            if release_date and len(release_date) >= 4:
                release_year = release_date[:4]
            else:
                release_year = None
            release_mbid = release.get('id')
        else:
            release_year = None

        cover_url = None
        if release_mbid:
            # Fetch the JSON listing of available cover art
            caa_url = f'https://coverartarchive.org/release/{release_mbid}/'
            caa_resp = requests.get(caa_url, headers={'Accept': 'application/json'}, timeout=10)
            if caa_resp.status_code == 200:
                caa_json = caa_resp.json()
                images = caa_json.get('images', [])
                for img in images:
                    if img.get('front', False):
                        cover_url = img.get('thumbnails', {}).get('500', img.get('image'))
                        break
                if not cover_url and images:
                    cover_url = images[0].get('thumbnails', {}).get('500', images[0].get('image'))

        time.sleep(1.2)

        return track_title, artist_name, album_title, release_year, cover_url

    except Exception as e:
        print(f"[MusicBrainz ERROR] {e}")
        return None, None, None, None, None


# Retrieve TVDB information for TV shows (requires API key!)
def fetch_tvdb(item_type, item_id):
    try:
        jwt = get_tvdb_jwt()
        if item_type == "series":
            url = f"https://api4.thetvdb.com/v4/series/{item_id}"
        elif item_type == "episode":
            url = f"https://api4.thetvdb.com/v4/episodes/{item_id}"
        else:
            raise ValueError("item_type must be 'series' or 'episode'")
        headers = {"Authorization": f"Bearer {jwt}"}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code != 200:
            return None
        data = resp.json().get('data', {})

        if item_type == "series":
            title = data.get('name', 'Unknown Series')
            overview = data.get('overview', '')
            poster_url = ''
            for art in data.get('artworks', []):
                if art.get('type') == 'poster':
                    poster_url = art.get('image')
                    break
            return title, overview, poster_url, item_id

        elif item_type == "episode":
            ep_title = data.get('name', '') or 'Unknown Episode'
            overview = data.get('overview', '')
            aired_season = data.get('seasonNumber', None)
            aired_episode = data.get('number', None)
            series_id = data.get('seriesId', None)
            series_name = ''
            poster_url = data.get('image', '')
            # Optionally fetch series info for name/poster if needed
            if series_id:
                series_info = fetch_tvdb("series", str(series_id))
                if series_info:
                    series_name = series_info[0]
                    if not poster_url:
                        poster_url = series_info[2]
            return ep_title, overview, poster_url, aired_season, aired_episode, series_name, series_id

    except Exception as e:
        print("[TVDB ERROR] %s" % e)
        return None

# Check if received input is TVDB Episode ID or not
def is_tvdb_episode_id(idstr):
    return idstr.isdigit() and 0 < int(idstr) < 99999999

# Fetch IMDB information via TMDB (requires API key!)
def fetch_tmdb_by_imdb(imdb_id):
    url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_API_KEY}&external_source=imdb_id"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None
        data = resp.json()
        results = data.get("movie_results", [])
        if not results:
            return None
        tmdb = results[0]
        title = tmdb.get("title", "Unknown Title")
        overview = tmdb.get("overview", "")
        poster_path = tmdb.get("poster_path", "")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        tmdb_id = tmdb.get("id", "")
        release_date = tmdb.get("release_date", "")
        director = tmdb.get("credits", "")
        year = release_date[:4] if release_date else ""
        return title, overview, poster_url, tmdb_id, year, director
    except Exception as e:
        print(f"[TMDB ERROR] {e}")
        return None


# Multiplayer information retrieval stuff below
def get_matching_rss_title(TitleName):
    feeds = {
        "Insignia": "https://ogxbox.org/rss/insignia.xml",
        "XLink Kai": "https://ogxbox.org/rss/xlinkkai.xml"
    }
    results = {}
    normalized_title = normalize(TitleName)

    for service, url in feeds.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall(".//item"):
                    title_elem = item.find("title")
                    if title_elem is not None:
                        raw_text = title_elem.text or ""
                        normalized_item_title = normalize(raw_text.split(":", 1)[0])
                        if normalized_item_title == normalized_title:
                            # Extract the stats after the first colon (unprocessed)
                            stats = raw_text.split(":", 1)[1].strip() if ":" in raw_text else ""
                            if stats:
                                results[service] = stats
                            break
        except Exception as e:
            print(f"Error reading RSS feed {url}: {e}")
            continue

    return results

def fetch_wiimmfi_online_players():
    url = "https://wiimmfi.de/stats/game"
    headers = {'User-Agent': 'sakuraPresence/1.0 ( contact: faithvoid@github or https://github.com/faithvoid )'}

    try:
        with requests.Session() as session:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            game_link = soup.find("a", href="/stats/game/mariokartwii")
            if not game_link:
                return None

            row = game_link.find_parent("tr")
            if not row:
                return None

            tds = row.find_all("td")
            if len(tds) < 5:
                return None

            online_players = tds[4].text.strip()
            return online_players

    except Exception as e:
        print("Error fetching Wiimmfi players:", e)
        return None

def fetch_xlink_gamelist():
    try:
        response = requests.get("https://api.teamxlink.co.uk/kai/GetGameList/v3", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"[XLink Kai] Error fetching game list: {e}")
        return None

def _find_xlink_game(search_value, search_by):
    gamelist = fetch_xlink_gamelist()
    if not gamelist or 'gamelist' not in gamelist or 'games' not in gamelist['gamelist']:
        return None

    search_value = search_value.upper()
    games = gamelist['gamelist']['games']

    for game in games:
        field = game.get('titleID' if search_by == 'id' else 'title', '').upper()
        if field == search_value:
            return game

    return None

def find_xlink_game(title_id):
    return _find_xlink_game(title_id, search_by='id')

def find_xlink_game_other(title_name):
    return _find_xlink_game(title_name, search_by='name')

def fetch_rpcn_page():
    try:
        resp = requests.get("https://rpcs3.net/rpcn", timeout=5)
        if resp.status_code == 200:
            return resp.text
        print(f"[RPCN] Error HTTP {resp.status_code}")
    except Exception as e:
        print(f"[RPCN] Exception fetching page: {e}")
    return None

def find_rpcn_game(search_value):
    html = fetch_rpcn_page()
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr', class_='darkmode-txt')

    search_value = search_value.strip().upper()
    for tr in rows:
        tds = tr.find_all('td')
        if len(tds) < 2:
            continue

        title = ''.join(tds[0].stripped_strings).upper()
        if title == search_value:
            players_raw = ''.join(tds[1].stripped_strings)  # e.g., "50 Online"
            player_count = ''.join(filter(str.isdigit, players_raw))
            return int(player_count) if player_count else 0

    return None

def fetch_ps4_cover_url(cusa_id):
    try:
        url = f"https://orbispatches.com/cusa/{cusa_id.lower()}"
        headers = {"User-Agent": "sakuraPresence/1.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return PS4_LOGO

        soup = BeautifulSoup(resp.text, "html.parser")
        meta = soup.find("meta", {"name": "twitter:image"})
        if meta and meta.get("content"):
            return meta["content"]

    except Exception as e:
        print(f"[ORBISPATCHES] Error fetching icon0 for {cusa_id}: {e}")
    return PS4_LOGO


# Clusterfuck of uncommented code ahoy! tl;dr this builds presence information depending on whether the information received is music, television, movies, or games.
def build_presence(dataIn):
    is_video = dataIn.get("video", False)
    is_music = dataIn.get("music", False)
    is_xbox = dataIn.get("xbox", False) or dataIn.get("game", False)
    is_ps1 = dataIn.get("ps1", False)
    is_ps2 = dataIn.get("ps2", False)
    is_ps3 = dataIn.get("ps3", False)
    is_ps4 = dataIn.get("ps4", False)
    is_psp = dataIn.get("psp", False)
    is_vita = dataIn.get("vita", False)
    is_wii = dataIn.get("wii", False)
    is_gc = dataIn.get("gc", False)
    is_dc = dataIn.get("dc", False)
    is_wiiu = dataIn.get("wiiu", False)
    is_switch = dataIn.get("switch", False)
    is_ds = dataIn.get("ds", False)
    is_3ds = dataIn.get("3ds", False)
    is_dashboard = dataIn.get("dashboard", False)
    is_xbox360 = dataIn.get("xbox360", False) or dataIn.get("Xenon", False)
    is_xboxone = dataIn.get("xboxone", False)
    xbmc_state = "Now Listening" if is_music else "Now Playing"
    idstr = dataIn.get("id", "")
    md5str = dataIn.get("md5", "")
    presenceData = {}
    log_string = ""

    # Weird fix for music presence issues. Music function takes priority above all else, if the received media isn't music, it defaults to TVDB/TMDB instead.
    if is_music:
        artist, track = split_artist_title(idstr)
        mb_title, mb_artist, mb_album, mb_cover = None, None, None, None
        if artist and track:
            mb_title, mb_artist, mb_album, mb_year, mb_cover = fetch_musicbrainz_info(artist, track)
        TitleName = f"{mb_artist}" if mb_title and mb_artist else idstr
        buttons = []
        if mb_artist and mb_title:
            if 'YouTube' in globals() and YouTube:
                yt_query = urllib.parse.quote(f"{mb_artist} {mb_title}")
                yt_url = f"https://www.youtube.com/results?search_query={yt_query}"
                buttons.append({"label": "Listen on YouTube", "url": yt_url})
            if 'Spotify' in globals() and Spotify:
                sp_query = urllib.parse.quote(f"{mb_artist} {mb_title}")
                sp_url = f"https://open.spotify.com/search/{sp_query}"
                buttons.append({"label": "Listen on Spotify", "url": sp_url})

        presenceData = {
            "type": 2,
            "details": TitleName,
            "state": track,
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": mb_cover if mb_cover else MUSIC_LARGE,
                "small_image": MUSIC_LARGE,
                "large_text": f"{mb_album} ({mb_year})" if mb_album and mb_year else TitleName,
                "small_text": f"{mb_artist} - {mb_title}",
            },
            "instance": True,
        }
        if buttons:
            presenceData["buttons"] = buttons
        log_string = f"Now Listening: {idstr} - {TitleName}"

    elif is_dashboard:
        id_upper = dataIn['id'].upper()

        dashboards = {
            "XBOXDASH": ("XBOX_DASHBOARD", "Xbox", XBOX_LOGO),
            "FFFE07D1": ("360_DASHBOARD", "Xbox 360", X360_LOGO),
            "X360DASH": ("360_DASHBOARD", "Xbox 360", X360_LOGO),
            "XONEDASH": ("XONE_DASHBOARD", "Xbox One", XONE_LOGO),
            "THESEUS": ("THESEUS", "Theseus", THESEUS_LOGO),
            "TEAMUIX": ("TEAMUIX", "UIX-Lite", UIX_LOGO),
            "XBMC4XBOX": ("XBOX MEDIA CENTER", "Xbox Media Center", XBMC_LOGO),
            "XBMC4GAMERS": ("XBMC4GAMERS", "XBMC4Gamers", XBMC4GAMERS_LOGO),
            "XBMCEMUSTATION": ("XBMCEMUSTATION", "XBMC-Emustation", XBMCEMUSTATION_LOGO),
            "CORTANAOS": ("CORTANAOS", "cortanaOS", CORTANAOS_LOGO),
            "AVALAUNCH": ("AVALAUNCH", "Avalaunch", AVALAUNCH_LOGO),
            "UNLEASHX": ("UNLEASHX", "UnleashX", UNLEASHX_LOGO),
            "PS1": ("PS2_DASHBOARD", "Playstation 1", PS1_LOGO),
            "PS2": ("PS2_DASHBOARD", "Playstation 2", PS2_LOGO),
            "PS3": ("PS3_DASHBOARD", "Playstation 3", PS3_LOGO),
            "PS4": ("PS4_DASHBOARD", "Playstation 4", PS4_LOGO),
            "PS5": ("PS4_DASHBOARD", "Playstation 4", PS5_LOGO),
            "PSP": ("PSP_DASHBOARD", "Playstation Portable", PSP_LOGO),
            "VITA": ("VITA_DASHBOARD", "Playstation Vita", VITA_LOGO),
            "DREAMCAST": ("DREAMCAST", "Sega Dreamcast", DC_LOGO),
            "DS": ("DS", "Nintendo DS", DS_LOGO),
            "3DS": ("3DS", "Nintendo 3DS", N3DS_LOGO),
            "SWITCH": ("3DS", "Nintendo Switch", SWITCH_LOGO),
            "WII": ("WII", "Nintendo Wii", WII_LOGO),
            "WIIU": ("WIIU", "Nintendo Wii U", WIIU_LOGO),
        }

        # Find matching dashboard or fallback
        match_key = next((key for key in dashboards if id_upper.startswith(key)), None)
        if match_key:
            XMID, TitleName, large_img = dashboards[match_key]
            presenceData = {
                "type": 0,
                "details": "Dashboard",
                "state": f"{TitleName}",
                "timestamps": {"start": int(time.time())},
                "assets": {
                    "large_image": large_img,
                },
                "instance": True,
            }
            log_string = f"{dataIn['id']} - {TitleName}"

    elif is_xbox360:

        inTitleID = idstr.upper() if idstr else md5str.upper()
        title = titles["xbox360"].get(inTitleID, dataIn.get("name", "Unknown Title"))
        xlink_game = find_xlink_game_other(title)
        status_info = get_matching_rss_title(title)
        xlink_users = status_info.get("XLink Kai")
        
        # Initialize arena URL
        encoded_arena_url = None
        
        # Use primaryVector directly if available
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})

        # Filter out blank services
        parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(parts) if parts else ""
        large_text = f"{title} (Xbox 360)"

        small_text_parts = []
        if "XLink Kai" in status_info:
           small_text_parts.append(f"XLink Kai: {status_info['XLink Kai']}")

        cdn_image_url = f"{X360_CDNURL}/{inTitleID[:4]}/{inTitleID}.png"
        homebrew_image_url = f"{X360_HOMEBREW_CDNURL}/{inTitleID}.png"
            
        try:
            resp = requests.head(cdn_image_url, timeout=3)
            if resp.status_code == 200:
                selected_image_url = cdn_image_url
            else:
                selected_image_url = homebrew_image_url
        except Exception as e:
            print(f"[Image Fallback] Error checking CDN image: {e}")
            selected_image_url = X360_LOGO

        presenceData = {
            "type": 0,
            "details": title,
            "state": "Xbox 360",
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": selected_image_url,
                "large_text": large_text,
                "small_image": X360_LOGO,
            },
            "instance": True,
        }

        buttons = [{"label": "Wikipedia", "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"}]
    
        if encoded_arena_url and not xtag:
            buttons.append({"label": "XLink Kai", "url": encoded_arena_url})
        if encoded_arena_url and xtag:
            buttons.append({"label": "XLink Kai" + f" [{xtag}]", "url": encoded_arena_url})
    
        if buttons:
            presenceData["buttons"] = buttons

        if small_text:
            presenceData["assets"]["small_text"] = small_text
        else:
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."

        if large_text and gamertag:
            presenceData["assets"]["large_text"] = f"{title} (Xbox 360) [{gamertag}]"
        else:
            presenceData["assets"]["large_text"] = large_text

        if not xlink_game and gamertag:
            presenceData["assets"]["small_text"] = f"Xbox 360 [Gamertag: {gamertag}]"



        elif not xlink_game:
            presenceData["assets"]["small_text"] = "Xbox 360"

        log_string = f"Now Playing: {inTitleID} - {title} (Xbox 360)"

    elif is_xboxone:
        inTitleID = idstr.upper()
        title = titles["xboxone"].get(inTitleID, dataIn.get("name", "Unknown Title"))
        xlink_game = find_xlink_game_other(title)
        status_info = get_matching_rss_title(title)
        xlink_users = status_info.get("XLink Kai")
        
        # Initialize arena URL
        encoded_arena_url = None
        
        # Use primaryVector directly if available
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})

        # Filter out blank services
        parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(parts) if parts else ""

        small_text_parts = []
        if "XLink Kai" in status_info:
           small_text_parts.append(f"XLink Kai: {status_info['XLink Kai']}")

        cdn_image_url = f"{XONE_CDNURL}/{inTitleID[:4]}/{inTitleID}.png"
        homebrew_image_url = f"{XONE_HOMEBREW_CDNURL}/{inTitleID}.png"
            
        try:
            resp = requests.head(cdn_image_url, timeout=3)
            if resp.status_code == 200:
                selected_image_url = cdn_image_url
            else:
                selected_image_url = homebrew_image_url
        except Exception as e:
            print(f"[Image Fallback] Error checking CDN image: {e}")
            selected_image_url = XONE_LOGO

        presenceData = {
            "type": 0,
            "details": title,
            "state": "Xbox One",
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": selected_image_url,
                "large_text": f"{title} (Xbox One)",
                "small_image": XONE_LOGO,
            },
            "instance": True,
            # Add buttons here
            "buttons": [
                {
                    "label": "View on XboxDB",
                    "url": f"https://xboxdb.altervista.org/game/{inTitleID}"
                },
                {
                    "label": "XLink Kai",
                    "url": encoded_arena_url
                }
            ]
        }

        if small_text:
            presenceData["assets"]["small_text"] = small_text
        else:
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."

        if not xlink_game:
            presenceData["assets"]["small_text"] = "Xbox One"

        log_string = f"Now Playing: {inTitleID} - {title} (Xbox One)"

    elif is_psp:
        inTitleID = idstr.upper()
        title = titles["psp"].get(inTitleID, dataIn.get("name", "Unknown Title"))
        xlink_game = find_xlink_game_other(title)
        status_info = get_matching_rss_title(title)
        xlink_users = status_info.get("XLink Kai")
    
        # Initialize arena URL
        encoded_arena_url = None
    
        # Use primaryVector if available
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})
    
        # Build presence text
        parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(parts) if parts else ""
    
        small_text_parts = []
        if "XLink Kai" in status_info:
            small_text_parts.append(f"XLink Kai: {status_info['XLink Kai']}")
    
        presenceData = {
            "type": 0,
            "details": title,
            "state": f"Playstation Portable",
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": f"{PSP_CDNURL}/{inTitleID}.png", 
                "large_text": f"{title} (Playstation Portable)",
                "small_image": PSP_LOGO,
            },
            "instance": True,
        }

        buttons = [{"label": "Wikipedia", "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"}]

        if encoded_arena_url and xtag:
            buttons.append({"label": "XLink Kai" + f" [{xtag}]", "url": encoded_arena_url})
        elif encoded_arena_url:
            buttons.append({"label": "XLink Kai", "url": encoded_arena_url})

        if buttons:
            presenceData["buttons"] = buttons
    
        if small_text:
            presenceData["assets"]["small_text"] = small_text
    
        if xlink_game and (not xlink_users or xlink_users.strip() in {"0", "None", ""}):
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."

        if not xlink_game:
            presenceData["assets"]["small_text"] = "Playstation Portable"
    
        log_string = f"Now Playing: {inTitleID} - {title} (Playstation Portable)"

    elif is_ps1:
        inTitleID = idstr.upper()
        title = titles["ps1"].get(inTitleID, dataIn.get("name", "Unknown Title"))
    
        presenceData = {
            "type": 0,
            "details": title,
            "timestamps": {"start": int(time.time())},
            "state": "Playstation",
            "assets": {
                "large_image": f"{PS1_CDNURL}/{inTitleID}.jpg",
                "large_text": f"{title} (Playstation)",
                "small_text": "Playstation",
                "small_image": PS1_LOGO,
            },
            "instance": True,
            "buttons": [
                {
                    "label": "Wikipedia",
                    "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"
                },
            ]
        }
    
        log_string = f"Now Playing: {inTitleID} - {title} (Playstation)"

    elif is_ps2:
        inTitleID = idstr.upper()
        title = titles["ps2"].get(inTitleID, dataIn.get("name", "Unknown Title"))
        xlink_game = find_xlink_game_other(title)
        status_info = get_matching_rss_title(title)
        xlink_users = status_info.get("XLink Kai")
    
        # Initialize arena URL
        encoded_arena_url = None
    
        # Use primaryVector if available
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})
    
        # Build presence text
        parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(parts) if parts else ""
    
        small_text_parts = []
        if "XLink Kai" in status_info:
            small_text_parts.append(f"XLink Kai: {status_info['XLink Kai']}")
    
        presenceData = {
            "type": 0,
            "details": title,
            "state": "Playstation 2",
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": f"{PS2_CDNURL}/{inTitleID}.jpg", 
                "large_text": f"{title} (Playstation 2)",
                "small_image": PS2_LOGO,
            },
            "instance": True,
        }

        buttons = [{"label": "Wikipedia", "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"}]

        if encoded_arena_url and xtag:
            buttons.append({"label": "XLink Kai" + f" [{xtag}]", "url": encoded_arena_url})
        elif encoded_arena_url:
            buttons.append({"label": "XLink Kai", "url": encoded_arena_url})

        if buttons:
            presenceData["buttons"] = buttons
    
        if small_text:
            presenceData["assets"]["small_text"] = small_text
    
        if xlink_game and (not xlink_users or xlink_users.strip() in {"0", "None", ""}):
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."

        if not xlink_game:
            presenceData["assets"]["small_text"] = "Playstation 2"
    
        log_string = f"Now Playing: {inTitleID} - {title} (Playstation 2)"

    elif is_ps3:
        inTitleID = idstr.upper()
        title = titles["ps3"].get(inTitleID, dataIn.get("name", "Unknown Title"))
    
        # Fetch multiplayer status
        status_info = get_matching_rss_title(title)
        xlink_game = find_xlink_game_other(title)
        rpcn_player_count = find_rpcn_game(title)
    
        # Prepare arena URL
        encoded_arena_url = None
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})
    
        # Combine network statuses
        if rpcn_player_count and rpcn_player_count > 0:
            status_info["RPCN"] = f"{rpcn_player_count} players"
        if rpcn_player_count and rpcn_player_count > 0 and rpcn_id:
            status_info["RPCN"] = f"{rpcn_player_count} players [{rpcn_id}]"
        if xlink_game and status_info.get("XLink Kai") in {"0", "None", "", None}:
            # If XLink Kai has no players, omit it
            status_info.pop("XLink Kai", None)
    
        # Generate small_text (e.g. "RPCN: 50 players | XLink Kai: 20 players")
        small_text_parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(small_text_parts)
        large_text = f"{title} (Playstation 3)"
    
        presenceData = {
            "type": 0,
            "details": title,
            "state": "Playstation 3",
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": f"{PS3_CDNURL}/{inTitleID}.JPG", 
                "large_text": large_text,
                "small_image": PS3_LOGO,
            },
            "instance": True,
        }

        if large_text and playstation_id:
            presenceData["assets"]["large_text"] = f"{title} (Playstation 3) [{playstation_id}]"
        else:
            presenceData["assets"]["large_text"] = large_text
    
        if small_text:
            presenceData["assets"]["small_text"] = small_text
        else:
            presenceData["assets"]["small_text"] = "No users connected on RPCN or XLink Kai."

        if not xlink_game and not rpcn_player_count:
            presenceData["assets"]["small_text"] = "Playstation 3"
    
        # Construct buttons
        buttons = [{"label": "Wikipedia", "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"}]
    
        if rpcn_player_count and rpcn_player_count > 0 and rpcn_id:
            buttons.append({"label": f"RPCN [{rpcn_id}]", "url": "https://rpcs3.net/rpcn"})
        elif rpcn_player_count and rpcn_player_count > 0:
            buttons.append({"label": "RPCN", "url": "https://rpcs3.net/rpcn"})
        if encoded_arena_url and xtag:
            buttons.append({"label": "XLink Kai" + f" [{xtag}]", "url": encoded_arena_url})
        elif encoded_arena_url:
            buttons.append({"label": "XLink Kai", "url": encoded_arena_url})

        if buttons:
            presenceData["buttons"] = buttons
    
        log_string = f"Now Playing: {inTitleID} - {title} (Playstation 3)"

    elif is_ps4:
        inTitleID = idstr.upper()
        title = titles["ps4"].get(inTitleID, dataIn.get("name", "Unknown Title"))
    
        # Fetch multiplayer status
        status_info = get_matching_rss_title(title)
        xlink_game = find_xlink_game_other(title)
    
        # Prepare arena URL
        encoded_arena_url = None
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})
    
        # Combine network statuses
        if xlink_game and status_info.get("XLink Kai") in {"0", "None", "", None}:
            # If XLink Kai has no players, omit it
            status_info.pop("XLink Kai", None)
    
        # Generate small_text (e.g. "RPCN: 50 players | XLink Kai: 20 players")
        small_text_parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(small_text_parts)
        large_text = f"{title} (Playstation 4)"

        # Try hashed cover URL
        cover_url = fetch_ps4_cover_url(inTitleID)
    
        presenceData = {
            "type": 0,
            "details": title,
            "state": "Playstation 4",
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": cover_url, 
                "large_text": large_text,
                "small_image": PS4_LOGO,
            },
            "instance": True,
        }

        if large_text and playstation_id:
            presenceData["assets"]["large_text"] = f"{title} (Playstation 4) [{playstation_id}]"
        else:
            presenceData["assets"]["large_text"] = large_text
    
        if small_text:
            presenceData["assets"]["small_text"] = small_text
        else:
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."

        if not xlink_game:
            presenceData["assets"]["small_text"] = "Playstation 4"
    
        # Construct buttons
        buttons = [{"label": "Wikipedia", "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"}]

        if encoded_arena_url and xtag:
            buttons.append({"label": "XLink Kai" + f" [{xtag}]", "url": encoded_arena_url})
        elif encoded_arena_url:
            buttons.append({"label": "XLink Kai", "url": encoded_arena_url})

        if buttons:
            presenceData["buttons"] = buttons
    
        log_string = f"Now Playing: {inTitleID} - {title} (Playstation 4)"

    elif is_vita:
        inTitleID = idstr.upper()
        title = titles["vita"].get(inTitleID, dataIn.get("name", "Unknown Title"))
    
        # Fetch multiplayer status
        status_info = get_matching_rss_title(title)
        xlink_game = find_xlink_game_other(title)
    
        # Prepare arena URL
        encoded_arena_url = None
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})
    
        # Combine network statuses
        if xlink_game and status_info.get("XLink Kai") in {"0", "None", "", None}:
            # If XLink Kai has no players, omit it
            status_info.pop("XLink Kai", None)
    
        # Generate small_text (e.g. "RPCN: 50 players | XLink Kai: 20 players")
        small_text_parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(small_text_parts)
        large_text = f"{title} (Playstation Vita)"
    
        presenceData = {
            "type": 0,
            "details": title,
            "state": "Playstation Vita",
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": f"{VITA_CDNURL}/{inTitleID}.png", 
                "large_text": f"{title} (Playstation Vita)",
                "small_image": VITA_LOGO,
            },
            "instance": True,
        }

        if large_text and playstation_id:
            presenceData["assets"]["large_text"] = f"{title} (Playstation Vita) [{playstation_id}]"
        else:
            presenceData["assets"]["large_text"] = large_text
    
        if small_text:
            presenceData["assets"]["small_text"] = small_text
        else:
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."
    
        # Construct buttons
        buttons = [{"label": "Wikipedia", "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"}]

        if encoded_arena_url and xtag:
            buttons.append({"label": "XLink Kai" + f" [{xtag}]", "url": encoded_arena_url})
        elif encoded_arena_url:
            buttons.append({"label": "XLink Kai", "url": encoded_arena_url})

        if buttons:
            presenceData["buttons"] = buttons

        if not xlink_game:
            presenceData["assets"]["small_text"] = "Playstation Vita"
    
        log_string = f"Now Playing: {inTitleID} - {title} (Playstation Vita)"

    elif is_switch:
        inTitleID = idstr.upper()
        title = titles["switch"].get(inTitleID, dataIn.get("name", "Unknown Title"))
    
        # Fetch multiplayer status
        status_info = get_matching_rss_title(title)
        xlink_game = find_xlink_game_other(title)
    
        # Prepare arena URL
        encoded_arena_url = None
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})
    
        # Combine network statuses
        if xlink_game and status_info.get("XLink Kai") in {"0", "None", "", None}:
            # If XLink Kai has no players, omit it
            status_info.pop("XLink Kai", None)
    
        # Generate small_text (e.g. "RPCN: 50 players | XLink Kai: 20 players")
        small_text_parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(small_text_parts)
        large_text = f"{title} (Nintendo Switch)"

        selected_image_url = None

        languages = [
            "EN", "US", "JA", "FR", "DE", "ES", "IT", "NL", "PT",
            "CH", "AU", "SE", "DK", "NO", "FI", "KO", "ZH", "RU"
        ]

        for lang in languages:
            cdn_image_url = f"{SWITCH_CDNURL}/{lang}/{inTitleID}.jpg"
            try:
                resp = requests.head(cdn_image_url, timeout=3)
                if resp.status_code == 200:
                    selected_image_url = cdn_image_url
                    break
            except Exception as e:
                print(f"[Image Fallback] Error checking {cdn_image_url}: {e}")
    
        presenceData = {
            "type": 0,
            "details": title,
            "state": "Nintendo Switch",
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": selected_image_url, 
                "large_text": large_text,
                "small_image": SWITCH_LOGO,
            },
            "instance": True,
        }

        if large_text and nintendo_id:
            presenceData["assets"]["large_text"] = f"{title} (Nintendo Switch) [{nintendo_id}]"
        else:
            presenceData["assets"]["large_text"] = large_text
    
        if small_text:
            presenceData["assets"]["small_text"] = small_text
        else:
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."

        if not xlink_game:
            presenceData["assets"]["small_text"] = "Nintendo Switch"
    
        # Construct buttons
        buttons = [{"label": "Wikipedia", "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"}]

        if encoded_arena_url and xtag:
            buttons.append({"label": "XLink Kai" + f" [{xtag}]", "url": encoded_arena_url})
        elif encoded_arena_url:
            buttons.append({"label": "XLink Kai", "url": encoded_arena_url})

        if buttons:
            presenceData["buttons"] = buttons
    
        log_string = f"Now Playing: {inTitleID} - {title} (Nintendo Switch)"

    elif is_wiiu:
        inTitleID = idstr.upper()
        title = titles["wiiu"].get(inTitleID, dataIn.get("name", "Unknown Title"))
        xlink_game = find_xlink_game_other(title)
        status_info = get_matching_rss_title(title)
        xlink_users = status_info.get("XLink Kai")

        # Arena URL
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})

        # Status text
        parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(parts) if parts else ""
        large_text = f"{title} (Wii U)"

        buttons = [
            {
                "label": "Wikipedia",
                "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"
            }
        ]
        
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            buttons.append({
                "label": "XLink Kai",
                "url": encoded_arena_url
            })

        languages = [
            "EN", "US", "JA", "FR", "DE", "ES", "IT", "NL", "PT",
            "CH", "AU", "SE", "DK", "NO", "FI", "KO", "ZH", "RU"
        ]

        selected_image_url = None

        for lang in languages:
            cdn_image_url = f"{WIIU_CDNURL}/{lang}/{inTitleID}.jpg"
            try:
                resp = requests.head(cdn_image_url, timeout=3)
                if resp.status_code == 200:
                    selected_image_url = cdn_image_url
                    break
            except Exception as e:
                print(f"[Image Fallback] Error checking {cdn_image_url}: {e}")
        

        presenceData = {
            "type": 0,
            "details": title,
            "state": "Wii U",
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": selected_image_url,
                "large_text": f"{title} (Wii U)",
                "small_text": small_text or "Wii U",
                "small_image": WIIU_LOGO,
            },
            "instance": True,
            "buttons": buttons,
        }

        if large_text and pretendo_id:
            presenceData["assets"]["large_text"] = f"{title} (Wii U) [{pretendo_id}]"
        else:
            presenceData["assets"]["large_text"] = large_text        

        if small_text:
            presenceData["assets"]["small_text"] = small_text
        else:
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."

        if not xlink_game:
            presenceData["assets"]["small_text"] = "Wii U"

        log_string = f"Now Playing: {inTitleID} - {title} (Wii U)"

    elif is_wii:
        inTitleID = idstr.upper()
        title = titles["gc-wii"].get(inTitleID, dataIn.get("name", "Unknown Title"))
        xlink_game = find_xlink_game_other(title)
        status_info = get_matching_rss_title(title)
        xlink_users = status_info.get("XLink Kai")
    
        online_players = fetch_wiimmfi_online_players()
        if online_players is None:
            current_players_text = "Online players: unavailable"
        else:
            current_players_text = f"Online players: {online_players}"
    
        # Arena URL
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
    
        # Status text - include current players info from Wiimmfi
        parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        if current_players_text not in parts:
            parts.append(current_players_text)
        small_text = " | ".join(parts) if parts else current_players_text
    
        buttons = [
            {
                "label": "Wikipedia",
                "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"
            }
        ]
    
        if xlink_game and 'primaryVector' in xlink_game:
            buttons.append({
                "label": "XLink Kai",
                "url": encoded_arena_url
            })

        languages = [
            "EN", "US", "JA", "FR", "DE", "ES", "IT", "NL", "PT",
            "CH", "AU", "SE", "DK", "NO", "FI", "KO", "ZH", "RU"
        ]

        selected_image_url = None

        for lang in languages:
            cdn_image_url = f"{WII_CDNURL}/{lang}/{inTitleID}.png"
            try:
                resp = requests.head(cdn_image_url, timeout=3)
                if resp.status_code == 200:
                    selected_image_url = cdn_image_url
                    break
            except Exception as e:
                print(f"[Image Fallback] Error checking {cdn_image_url}: {e}")
    
        presenceData = {
            "type": 0,
            "state": "Wii",
            "details": title,
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": selected_image_url, 
#                "large_image": f"{WII_CDNURL}/{inTitleID[:3]}/{inTitleID}.png", 
#                "large_image": f"{WII_CDNURL}/{inTitleID}.png", 
                "large_text": f"{title} (Wii)",
                "small_text": small_text or "Wii",
                "small_image": WII_LOGO,
            },
            "instance": True,
            "buttons": buttons,
        }
    
        if small_text:
            presenceData["assets"]["small_text"] = small_text
        else:
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."

        if not xlink_game:
            presenceData["assets"]["small_text"] = "Wii"
    
        log_string = f"Now Playing: {inTitleID} - {title} (Wii)"

    elif is_gc:
        inTitleID = idstr.upper()
        title = titles["gc-wii"].get(inTitleID, dataIn.get("name", "Unknown Title"))
        xlink_game = find_xlink_game_other(title)
        status_info = get_matching_rss_title(title)
        xlink_users = status_info.get("XLink Kai")

        # Arena URL
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})

        # Status text
        parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(parts) if parts else ""

        buttons = [
            {
                "label": "Wikipedia",
                "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"
            }
        ]
        
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            buttons.append({
                "label": "XLink Kai",
                "url": encoded_arena_url
            })

        languages = [
            "EN", "US", "JA", "FR", "DE", "ES", "IT", "NL", "PT",
            "CH", "AU", "SE", "DK", "NO", "FI", "KO", "ZH", "RU"
        ]

        selected_image_url = None

        for lang in languages:
            cdn_image_url = f"{GC_CDNURL}/{lang}/{inTitleID}.png"
            try:
                resp = requests.head(cdn_image_url, timeout=3)
                if resp.status_code == 200:
                    selected_image_url = cdn_image_url
                    break
            except Exception as e:
                print(f"[Image Fallback] Error checking {cdn_image_url}: {e}")

        presenceData = {
            "type": 0,
                
            "state": "Gamecube",
            "timestamps": {"start": int(time.time())},
            "details": title,
            "assets": {
                "large_image": selected_image_url,
#                "large_image": f"{GC_CDNURL}/{inTitleID[:3]}/{inTitleID}.png", 
#                "large_image": f"{GC_CDNURL}/{inTitleID}.png",
                "large_text": f"{title} (Gamecube)",
                "small_text": small_text or "Gamecube",
                "small_image": GC_LOGO,
            },
            "instance": True,
            "buttons": buttons,
        }
        

        if small_text:
            presenceData["assets"]["small_text"] = small_text
        else:
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."

        if not xlink_game:
            presenceData["assets"]["small_text"] = "Gamecube"

        log_string = f"Now Playing: {inTitleID} - {title} (Gamecube)"

    elif is_ds:
        inTitleID = idstr.upper()
        title = titles["ds"].get(inTitleID, dataIn.get("name", "Unknown Title"))
        xlink_game = find_xlink_game_other(title)
        status_info = get_matching_rss_title(title)
        xlink_users = status_info.get("XLink Kai")

        # Arena URL
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})

        # Status text
        parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(parts) if parts else ""

        buttons = [
            {
                "label": "Wikipedia",
                "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"
            }
        ]
        
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            buttons.append({
                "label": "XLink Kai",
                "url": encoded_arena_url
            })

        languages = [
            "EN", "US", "JA", "FR", "DE", "ES", "IT", "NL", "PT",
            "CH", "AU", "SE", "DK", "NO", "FI", "KO", "ZH", "RU"
        ]

        selected_image_url = None

        for lang in languages:
            cdn_image_url = f"{DS_CDNURL}/{lang}/{inTitleID}.jpg"
            try:
                resp = requests.head(cdn_image_url, timeout=3)
                if resp.status_code == 200:
                    selected_image_url = cdn_image_url
                    break
            except Exception as e:
                print(f"[Image Fallback] Error checking {cdn_image_url}: {e}")

        presenceData = {
            "type": 0,
                
            "state": "Nintendo DS",
            "timestamps": {"start": int(time.time())},
            "details": title,
            "assets": {
                "large_image": selected_image_url, 
                "large_text": f"{title} (Nintendo DS)",
                "small_text": small_text or "Nintendo DS",
                "small_image": DS_LOGO,
            },
            "instance": True,
            "buttons": buttons,
        }
        
        if small_text:
            presenceData["assets"]["small_text"] = small_text
        else:
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."

        if not xlink_game:
            presenceData["assets"]["small_text"] = "Nintendo DS"

        log_string = f"Now Playing: {inTitleID} - {title} (Nintendo DS)"

    elif is_3ds:
        inTitleID = idstr.upper()
        title = titles["3ds"].get(inTitleID, dataIn.get("name", "Unknown Title"))
        xlink_game = find_xlink_game_other(title)
        status_info = get_matching_rss_title(title)
        xlink_users = status_info.get("XLink Kai")

        # Arena URL
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})

        # Status text
        parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(parts) if parts else ""
        large_text = f"{title} (Nintendo 3DS)"

        buttons = [
            {
                "label": "Wikipedia",
                "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"
            }
        ]
        
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            buttons.append({
                "label": "XLink Kai",
                "url": encoded_arena_url
            })

        languages = [
            "EN", "US", "JA", "FR", "DE", "ES", "IT", "NL", "PT",
            "CH", "AU", "SE", "DK", "NO", "FI", "KO", "ZH", "RU"
        ]

        selected_image_url = None

        for lang in languages:
            cdn_image_url = f"{N3DS_CDNURL}/{lang}/{inTitleID}.jpg"
            try:
                resp = requests.head(cdn_image_url, timeout=3)
                if resp.status_code == 200:
                    selected_image_url = cdn_image_url
                    break
            except Exception as e:
                print(f"[Image Fallback] Error checking {cdn_image_url}: {e}")

        presenceData = {
            "type": 0,
                
            "state": "Nintendo 3DS",
            "timestamps": {"start": int(time.time())},
            "details": title,
            "assets": {
                "large_image": selected_image_url, 
                "large_text": large_text,
                "small_text": small_text or "Nintendo 3DS",
                "small_image": N3DS_LOGO,
            },
            "instance": True,
            "buttons": buttons,
        }

        if large_text and pretendo_id:
            presenceData["assets"]["large_text"] = f"{title} (Nintendo 3DS) [{pretendo_id}]"
        else:
            presenceData["assets"]["large_text"] = large_text        

        if small_text:
            presenceData["assets"]["small_text"] = small_text
        else:
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."

        if not xlink_game:
            presenceData["assets"]["small_text"] = "Nintendo 3DS"

        log_string = f"Now Playing: {inTitleID} - {title} (Nintendo 3DS)"

    elif is_dc:
        inTitleID = idstr.upper()
        title = titles["dc"].get(inTitleID, dataIn.get("name", "Unknown Title"))
        xlink_game = find_xlink_game_other(title)
        status_info = get_matching_rss_title(title)
        xlink_users = status_info.get("XLink Kai")

        # Arena URL
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})

        # Status text
        parts = [f"{service}: {info}" for service, info in status_info.items() if info]
        small_text = " | ".join(parts) if parts else ""

        buttons = [
            {
                "label": "Wikipedia",
                "url": f"https://wikipedia.com/wiki/{urllib.parse.quote(title)}"
            }
        ]
        
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            buttons.append({
                "label": "XLink Kai",
                "url": encoded_arena_url
            })

        presenceData = {
            "type": 0,
                
            "state": "Dreamcast",
            "timestamps": {"start": int(time.time())},
            "details": title,
            "assets": {
                "large_image": f"{DC_CDN}/{inTitleID}.png",
                "large_text": f"{title} (Dreamcast)",
                "small_text": small_text or "Dreamcast",
                "small_image": DC_LOGO,
            },
            "instance": True,
            "buttons": buttons,
        }
        

        if xlink_game and (not xlink_users or xlink_users.strip() in {"0", "None", ""}):
            presenceData["assets"]["small_text"] = "No users connected on XLink Kai."

        log_string = f"Now Playing: {inTitleID} - {title} (Dreamcast)"
    

    elif is_valid_imdb_id(idstr):
        tmdb = fetch_tmdb_by_imdb(idstr)
        if tmdb:
            title, overview, poster_url, tmdb_idm, year, director = tmdb
            display_title = f"{title} ({year})" if year else title
            if overview and overview.strip():
                small_text = overview[:125] + "..." if len(overview) > 128 else overview
            else:
                small_text = "Media info not found."
            presenceData = {
                "type": 3,
                "details": display_title,
                "state": small_text,
                "timestamps": {"start": int(time.time())},
                "assets": {
                    "large_image": poster_url if poster_url else XBMC_LOGO,
                    "large_text": display_title,
                    "small_image": VIDEO_LARGE,
                    "small_text": small_text,
                },
                "instance": True,
                "buttons": [{"label": "View on IMDb", "url": f"https://www.imdb.com/title/{idstr}"}],
            }
            log_string = f"Now Playing: {idstr} - {title}"
        else:
            fallback_title = fallback_title_from_filename(idstr) if is_filename(idstr) else idstr
            presenceData = {
                "type": 3,
                "details": fallback_title,
                "state": "Unlisted content",
                "timestamps": {"start": int(time.time())},
                "assets": {
                    "large_image": XBMC_LOGO,
                    "large_text": "Media info not found.",
                    "small_image": VIDEO_LARGE,
                },
                "instance": True,
            }
            log_string = f"Now Playing: {idstr} - {fallback_title}"

    elif is_tvdb_episode_id(idstr) and not is_xbox:
        tvdb_ep = fetch_tvdb("episode", idstr)
        if tvdb_ep:
            ep_title, overview, poster_url, aired_season, aired_episode, series_name, series_id = tvdb_ep
            if overview and overview.strip():
                small_text = overview[:125] + "..." if len(overview) > 128 else overview
            else:
                small_text = "Media info not found."
            season_str = f"{int(aired_season):02d}" if aired_season is not None else "??"
            episode_str = f"{int(aired_episode):02d}" if aired_episode is not None else "??"
            details_text = f"{series_name}"
            presenceData = {
                "type": 3,
                "details": details_text,
                "state": f"{ep_title} (S{int(aired_season):02d}E{int(aired_episode):02d})",
                "timestamps": {"start": int(time.time())},
                "assets": {
                    "large_image": poster_url if poster_url else XBMC_LOGO,
                    "large_text": f"{details_text} - {ep_title} (S{season_str}E{episode_str})",
                    "small_text": small_text,
                    "small_image": VIDEO_LARGE,
                },
                "instance": True,
                "buttons": [{"label": "View on TVDB", "url": f"https://www.thetvdb.com/series/{series_id}/episodes/{idstr}"}],
            }
            log_string = f"Now Playing: {idstr} - {details_text}"
        else:
            fallback_title = fallback_title_from_filename(idstr) if is_filename(idstr) else idstr
            presenceData = {
                "type": 3,
                "details": fallback_title,
                "state": "Unlisted content",
                "timestamps": {"start": int(time.time())},
                "assets": {
                    "large_image": XBMC_LOGO,
                    "large_text": "Media info not found.",
                    "small_image": VIDEO_LARGE,
                },
                "instance": True,
            }
            log_string = f"Now Playing: {idstr} - {fallback_title}"

    elif is_video:
        fallback_title = fallback_title_from_filename(idstr) if is_filename(idstr) else idstr
        xbmc_state = "Now Playing"
        presenceData = {
            "type": 3,
            "details": fallback_title,
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_text": "Video info not found.",
                "small_image": VIDEO_LARGE,
            },
            "instance": True,
        }
        log_string = f"{xbmc_state} {idstr} - {fallback_title}"

    elif is_music:
        fallback_title = fallback_title_from_filename(idstr) if is_filename(idstr) else idstr
        xbmc_state = "Now Listening"
        presenceData = {
            "type": 2,
            "details": fallback_title,
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": MUSIC_LARGE,
                "large_text": "Music info not found.",
                "small_image": MUSIC_LARGE,
            },
            "instance": True,
        }
        log_string = f"{xbmc_state} {idstr} - {fallback_title}"
    
    elif is_xbox:
        XMID, TitleName = lookupID(dataIn.get('id')) if dataIn.get("id") else lookupID(dataIn.get('md5'))
        inTitleID = (dataIn.get('id') or dataIn.get('md5', '')).upper()
        xlink_game = find_xlink_game(inTitleID)
    
        # Initialize arena URL
        encoded_arena_url = None
    
        if xlink_game and 'primaryVector' in xlink_game:
            encoded_arena_url = f"xlinkkai://{urllib.parse.quote(xlink_game['primaryVector'])}"
            print({encoded_arena_url})
    
        # Get player stats
        status_info = get_matching_rss_title(TitleName)
    
        # Build small_text_parts from active services and IDs
        small_text_parts = []
        if "Insignia" in status_info and insignia_id:
            small_text_parts.append(f"Insignia: {status_info['Insignia']}")
        if "XLink Kai" in status_info and xtag:
            small_text_parts.append(f"XLink Kai: {status_info['XLink Kai']}")
        small_text = " | ".join(small_text_parts) if small_text_parts else ""
        large_text = f"{TitleName} (Xbox)",
    
        cdn_image_url = f"{XBOX_CDNURL}/{inTitleID[:4]}/{inTitleID}.png"
        homebrew_image_url = f"{XBOX_HOMEBREW_CDNURL}/{inTitleID}.png"
    
        try:
            resp = requests.head(cdn_image_url, timeout=3)
            if resp.status_code == 200:
                selected_image_url = cdn_image_url
            else:
                selected_image_url = homebrew_image_url
        except Exception as e:
            print(f"[Image Fallback] Error checking CDN image: {e}")
            selected_image_url = XBOX_LOGO
    
        presenceData = {
            "type": 0,
            "details": TitleName,
            "state": "Xbox",
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image": selected_image_url,
                "large_text": large_text,
                "small_image": "https://cdn.discordapp.com/avatars/1304454011503513600/6be191f921ebffb2f9a52c1b6fc26dfa",
            },
            "instance": True,
        }

        if large_text and insignia_id:
            presenceData["assets"]["large_text"] = f"{TitleName} (Xbox) [{insignia_id}]"
        else:
            presenceData["assets"]["large_text"] = large_text
    
        if small_text:
            presenceData["assets"]["small_text"] = small_text
    
        if "XLink Kai" not in status_info and "Insignia" not in status_info and not small_text:
            presenceData["assets"]["small_text"] = "No users connected on Insignia or XLink Kai."

        if not xlink_game:
            presenceData["assets"]["small_text"] = "Xbox"
    
        if XMID != "00000000":
            if insignia_id:
                buttons = [{"label": f"Insignia [{insignia_id}]", "url": f"https://insignia.live/games/{inTitleID}"}]
            else:
                buttons = [{"label": "Insignia", "url": f"https://insignia.live/games/{inTitleID}"}]
            if encoded_arena_url and xtag:
                buttons.append({"label": "XLink Kai" + f" [{xtag}]", "url": encoded_arena_url})
            elif encoded_arena_url:
                buttons.append({"label": "XLink Kai", "url": encoded_arena_url})
            presenceData["buttons"] = buttons
        elif 'name' in dataIn and dataIn['name'] and not Insignia:
            presenceData['details'] = dataIn['name']
    
        log_string = f"Now Playing: {TitleName} (Xbox)"

    return presenceData, log_string

# Check if the received information is a filename or not
def is_filename(idstr):
    idstr = idstr.lower()
    return idstr.endswith('.mkv') or idstr.endswith('.mp4') or idstr.endswith('.avi')

# Generate fallback video title from filename.
def fallback_title_from_filename(filename):
    name = os.path.splitext(os.path.basename(filename))[0]
    name = re.sub(r'[._-]+', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip().title()

# Check if received input is IMDB ID or not
def is_valid_imdb_id(imdb_id):
    return bool(re.fullmatch(r"tt\d{7,}", imdb_id))

# Get local IP address
def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('255.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return '.'.join(IP.split('.'))

# Look up Xbox Title IDs via MobCat's API
def lookupID(titleID):
    if not titleID:
        return "00000000", "Unknown Title"

    titleID_upper = titleID.upper()
    XMID, TitleName = "00000000", "Unknown Title"

    # Check if it's an MD5 hash (32-character hex string)
    is_md5 = len(titleID_upper) == 32 and all(c in "0123456789ABCDEF" for c in titleID_upper)

    if not is_md5:
        # Only query the API if it's NOT an MD5 (likely a Title ID)
        try:
            with urllib.request.urlopen(f"{XBOX_APIURL}/api.php?id={titleID_upper}") as url:
                apiData = json.load(url)
                if 'error' not in apiData:
                    XMID = apiData[0]['XMID']
                    TitleName = apiData[0]['Full_Name']
        except Exception as e:
            print(f"[lookupID] API Error for {titleID_upper}: {e}")

    # Fallback to homebrew titles (MD5 or Title ID)
    if TitleName == "Unknown Title":
        # Check homebrew_xbox titles (for Title IDs)
        TitleName = titles['xbox'].get(titleID_upper, "Unknown Title")
        
        # If still not found and it's an MD5, check md5["homebrew_xbox"]
        if TitleName == "Unknown Title" and is_md5:
            TitleName = md5['xbox'].get(titleID_upper, "Unknown Title")

    return XMID, TitleName

# Clusterfuck of uncommented code ahoy!
async def clientHandler(websocket: wetSocks):
    try:
        print(f"{int(time.time())} {websocket.remote_address} Xbox connected!")
        async for message in websocket:
            print(f"{int(time.time())} {websocket.remote_address} {message}")
            if message == "" or message == "{}":
                print(f"{int(time.time())} {websocket.remote_address} Clear Presence signal received.")
                presence.clear()
                continue
            dataIn = json.loads(message)
            if not dataIn.get("id") and not dataIn.get("md5"):
                print(f"[WebSocket] Clear signal received from {websocket.remote_address}, clearing presence.")
                presence.clear()
                continue
            presenceData, log_string = build_presence(dataIn)
            presence.set(presenceData)
            print(f"[WebSocket] {log_string}")
    except websockets.ConnectionClosedOK:
        print(f"{int(time.time())} {websocket.remote_address} Client disconnected normally")
    except websockets.ConnectionClosedError as e:
        print(f"{int(time.time())} {websocket.remote_address} Client disconnected with error: {e}")
    finally:
        if websocket.closed:
            print(f"{int(time.time())} {websocket.remote_address} Connection closed. Presence cleared.")
            presence.clear()

# UDP Listener
def listen_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 1102))  # Same port as WebSocket
    print("[UDP] Listening for raw relay packets on port 1102...")

    while True:
        data, addr = sock.recvfrom(1024)
        try:
            message = data.decode("utf-8").strip()
            if message == "XBDSTATS_ONLINE":
                continue
            print(f"[UDP] From {addr}: {message}")
            dataIn = json.loads(message)
            if not dataIn.get("id") and not dataIn.get("md5"):
                print(f"[UDP] Clear signal received from {addr}, clearing presence.")
                presence.clear()
                continue
            presenceData, log_string = build_presence(dataIn)
            presence.set(presenceData)
            print(f"[UDP] {log_string}")
        except Exception as e:
            print(f"[UDP ERROR] {e}")

# TCP Listener
def listen_tcp():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('0.0.0.0', 1103))
    server_sock.listen(5)
    print("[TCP] Listening for raw relay packets on port 1103...")

    while True:
        try:
            conn, addr = server_sock.accept()
            threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True).start()
        except Exception as e:
            print(f"[TCP ERROR] Accept error: {e}")

def handle_tcp_client(conn, addr):
    print(f"[TCP] Connection from {addr}")
    buffer = ""
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buffer += data.decode("utf-8")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    print(f"[TCP] From {addr}: {line}")
                    dataIn = json.loads(line)
                    if not dataIn.get("id") and not dataIn.get("md5"):
                        print(f"[TCP] Clear signal received from {addr}, clearing presence.")
                        presence.clear()
                        continue
                    presenceData, log_string = build_presence(dataIn)
                    presence.set(presenceData)
                    print(f"[TCP] {log_string}")
                except Exception as e:
                    print(f"[TCP ERROR] {e}")
    except Exception as e:
        print(f"[TCP ERROR] Connection error from {addr}: {e}")
    finally:
        conn.close()
        print(f"[TCP] Connection closed from {addr}")

# Fetch MOTD
def fetch_motd(url):
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode().strip()
    except Exception as e:
        return f"[MOTD fetch error: {e}]"

# Checks for updates and notifies the user when a new version is available.
def check_for_update(local_path="version.txt", remote_url="https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/version.txt"):
    try:
        with urllib.request.urlopen(remote_url) as response:
            remote_version = response.read().decode("utf-8").strip()

        if not os.path.exists(local_path):
            return

        with open(local_path, "r", encoding="utf-8") as f:
            local_version = f.read().strip()

        if remote_version > local_version:
            print('\033]8;;https://github.com/faithvoid/sakuraPresence\033\\[Update Available]\033]8;;\033\\\n')

    except Exception:
        pass

# Main async WebSocket server entry point
async def main():
    serverIP = getIP()
    server = await websockets.serve(clientHandler, serverIP, 1102)
    print(f"Server started on ws://{serverIP}:1102\nWaiting for connection...")

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        presence.close()
        server.close()
        await server.wait_closed()
        print("Server closed")
        exit()

# Banner + MOTD + launch

motd_url = "https://raw.githubusercontent.com/faithvoid/sakuraPresence/refs/heads/main/motd.txt"
motd = fetch_motd(motd_url)

print('''
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠴⠛⠲⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⡴⠋⠛⠯⣀⠠⡀⠘⣇⠀⣠⠦⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢀⣀⣀⣀⢠⠏⠀⠀⠀⠀⠈⢷⢧⡆⢸⣰⠃⠀⠹⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢠⡏⠀⠀⠈⢹⡄⠀⡀⢧⢠⠀⢸⣾⣇⡼⠃⠀⠀⠀⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣞⠁⠀⠀⢄⠀⢻⡄⠹⡌⢯⡇⢸⣿⠋⠀⠀⡴⠀⢀⡏⠀⢐⣶⣤⠴⠞⢳⠀⠀⠀⠀⠀⣴⠒⠒⠋⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠘⣧⠀⠀⢄⡑⢤⡙⣦⡹⣾⣧⣼⣃⢠⣦⠞⠀⢠⡞⠀⠀⣼⣿⠅⠀⣴⡾⠀⠀⠀⠀⡼⠁⠀⠀⠀⠀⢻⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀
⠀⠈⣳⡴⠖⠚⠛⠻⠿⣿⣾⣿⣿⣿⣿⣤⣾⡶⠋⠛⢦⠀⣿⣿⣠⣾⡿⠃⠀⠀⡤⢼⣅⠀⡄⢸⠀⣰⠋⠁⠀⠀⠉⠹⣄⠀⠀⠀⠀
⠀⠀⠙⠦⣄⡀⠀⠀⠈⠉⣿⣿⣿⣿⠋⠉⣯⣁⡀⣀⣴⣧⡿⠟⠙⠉⠀⣤⠤⢀⡇⠀⠈⢷⡇⡇⣸⠁⡀⠀⡄⠀⠀⠀⡏⠉⠓⢦⠀
⠀⠀⢠⠞⠁⠉⢹⣶⣶⣶⠋⠙⠁⢀⣠⣴⣋⠀⠀⢧⣽⣿⣀⣀⡀⠀⠀⢻⢄⠀⣧⠀⠸⡌⢿⢣⠇⡴⢡⣾⠖⠀⢀⡼⣡⠆⢀⡾⠀
⠀⠀⠈⠉⠓⠺⠿⠖⠛⢙⡷⠶⣺⡿⠁⡇⠙⠻⢶⣼⡟⠘⣇⢨⣙⣦⡀⠘⢯⡻⣾⣞⢆⢻⣞⣿⣼⣷⠟⢁⣠⣴⣯⣾⠗⣠⡞⠁⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢰⠏⢀⢿⠏⣡⠞⡽⢦⡀⠀⢻⣧⠀⠈⠛⠿⢿⣷⡀⢀⣹⢻⠟⠦⣿⣿⣿⣿⣿⡟⠛⠛⠛⠻⠤⠾⠥⠴⠶⡄
⠀⠀⠀⠀⠀⠀⠀⠀⡟⠀⣡⠼⠛⠁⣸⠃⠀⠹⡄⠀⠛⢷⣄⣰⣄⠀⠹⣿⡿⡼⢸⡄⠀⠘⠻⢻⢿⣿⠛⠤⠄⠀⠀⠀⠀⠀⠀⣴⠃
⠀⠀⠀⠀⠀⠀⠀⠀⢷⠟⠁⠀⠀⡴⣿⣠⢖⢋⡇⠀⠀⠈⢻⣿⣟⣧⢠⡿⠋⢁⣰⡟⠓⢦⡀⠀⣠⣿⣿⣆⣀⠀⠀⠀⣀⡤⠞⠁⠀
⠀⠀⠀⠀⠀⠀⣀⡤⠴⣶⣤⣄⡀⠙⢿⣿⣿⡼⠁⠀⠀⠀⢸⡏⢻⣿⣿⣥⡶⠟⠛⠻⣷⣶⣭⡉⠹⣄⠛⡆⣿⠉⠉⠉⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠘⢧⡀⠀⠈⠉⣿⣿⣦⣀⣈⣿⠁⠀⠀⠀⢀⡼⢧⣀⣿⡿⠋⠀⠀⠀⠀⠸⣎⣻⣿⡄⠘⢦⡤⠏⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢹⣷⣶⣾⠿⠟⢉⡁⠉⠻⣦⡤⠤⣼⠉⠀⠀⠙⣯⠀⠀⣀⠀⠀⠀⠀⠀⠉⠻⠇⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⢠⣶⣯⣿⣿⠿⡷⠋⠀⠀⠀⠙⢦⡰⡄⢸⣄⡼⠉⢹⡄⠀⠀⠀⠀⠀⠀⢀⣾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠛⠛⠛⢾⡅⠀⠀⢄⢀⠀⠀⣷⣿⢘⡿⠁⠀⠀⢷⠀⠀⠀⠀⠀⠀⠨⠨⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡆⠀⠀⡀⠀⢷⡀⢰⡈⣏⣆⠀⢸⡿⠋⠀⢀⠀⠀⣸⠀⠀⠀⠀⠀⠀⠠⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⠀⠀⠈⠢⡈⢳⣄⠳⡜⣾⡀⣿⠁⣀⣠⠋⠀⣰⠇⠀⠀⠀⠀⠀⣀⡄⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⣀⣈⣑⣮⣷⣽⣦⣹⣿⣿⣿⣾⡋⣡⣦⡼⠧⣄⠀⣟⣦⠖⠛⢩⡇⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣏⠀⠀⠀⠀⠈⠭⣽⣿⣿⣿⡟⠛⣿⠃⠀⠀⠈⣾⣿⡗⠀⣠⣿⣇⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠟⠲⠤⢤⣄⣠⡼⠿⠟⠛⠁⢀⡿⠓⠈⠉⠈⢹⣿⣧⣾⡿⢋⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠷⢤⣀⣒⣻⡿⠟⢦⣈⣠⣶⣿⣿⡇⠀⠀⠀⢀⣼⠟⣁⡤⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡿⣾⡁⡟⣿⠃⣠⣤⡶⠟⢻⣿⣿⣯⡟⠿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠻⣁⡷⢳⣿⣼⡟⠁⠀⠀⠀⠙⢮⣛⡗⠀⠈⣳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠟⠉⠀⢸⣿⣟⣴⣾⣉⡛⠲⣄⠀⠉⠙⠒⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠁⠈⠳⣜⢯⠳⣌⠻⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠈⠛⠲⠦⠤⢿⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

[''' + 
    '\033]8;;https://github.com/OfficialTeamUIX/Xbox-Discord-Rich-Presence\033\\sakuraPresence v1.0 - Retro Discord Rich Presence\033]8;;\033\\' +
''']

by [''' + 
    '\033]8;;https://github.com/faithvoid\033\\faithvoid\033]8;;\033\\ + ' +
    '\033]8;;https://github.com/MrMilenko\033\\milenko\033]8;;\033\\ + ' +
    '\033]8;;https://github.com/MobCat\033\\mobcat\033]8;;\033\\' +
''']

''')

check_for_update()

threading.Thread(target=broadcast_online, daemon=True).start()
threading.Thread(target=listen_udp, daemon=True).start()
threading.Thread(target=listen_tcp, daemon=True).start()

#threading.Thread(target=poll_xbox360_jrpc, args=({X360_ADDRESS}, SCAN_INTERVAL), daemon=True).start()
#threading.Thread(target=poll_ps3_webman, args=("{PS3_ADDRESS}", SCAN_INTERVAL), daemon=True).start()

asyncio.run(main())
