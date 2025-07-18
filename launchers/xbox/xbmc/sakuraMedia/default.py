# sakuraMedia - Discord Rich Presence script for XBMC4Xbox / XBMC4Gamers (and possibly XBMC360). For use with sakuraPresence. (https://github.com/faithvoid/sakuraPresence)
# Based on xbdStats by MobCat and Milenko
# To use on startup, add xbmc.executebuiltin("XBMC.RunScript(Q:/scripts/MediaPresence/default.py)") to "autoexec.py" in your XBMC "scripts" folder (usually Q:/scripts)
  
import xbmc
import socket
import json
import time
import os
import xml.etree.ElementTree as ET
from collections import OrderedDict
import xbmcaddon

addon = xbmcaddon.Addon()
dashboard_enabled = True
dashboard_type = "cortanaOS"
SERVER_PORT = 1102
SERVER_IP = addon.getSetting("SERVER_IP")

# Listen for "XBDSTATS_ONLINE" and automagically connect.
def discover_server(timeout=10):
    """Listen for XBDSTATS_ONLINE UDP broadcasts and return the sender's IP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', SERVER_PORT))
    sock.settimeout(timeout)
    print('Waiting for XBDSTATS_ONLINE broadcast...')
    try:
        while True:
            data, addr = sock.recvfrom(4096)
            if data == b'XBDSTATS_ONLINE':
                xbmc.executebuiltin('XBMC.Notification("sakuraMedia", "sakuraPresence server found!", 4000, icon-cortana.png)')
                return addr[0]
    except socket.timeout:
        xbmc.executebuiltin('XBMC.Notification("sakuraMedia", "sakuraPresence server not found, please restart the server / client and try again.", 5000, icon-cortana.png)')
        return None
    finally:
        sock.close()

# Send payload to the xbdStats server
def send_to_server(idval, season=None, episode=None, media_type=None, server_ip="127.0.0.1"):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        payload_data = OrderedDict([('id', idval)])
        if media_type:
            payload_data[media_type] = True
        if season is not None:
            payload_data['season'] = season
        if episode is not None:
            payload_data['episode'] = episode
        payload = json.dumps(payload_data, separators=(',', ':'))
        sock.sendto(payload.encode('utf-8'), (server_ip, SERVER_PORT))
        sock.close()
    except:
        pass

def is_music_playing():
    try:
        player = xbmc.Player()
        return player.isPlayingAudio()
    except:
        return False

# Extracts TVDB/IMDB ID information from a matching NFO file (if available) and sends it. Fallbacks are under "get_now_playing".
def extract_ids_from_nfo(nfo_path):
    try:
        if not os.path.isfile(nfo_path):
            return None, None, None

        tree = ET.parse(nfo_path)
        root = tree.getroot()
        ids = []

        for tag in ['id', 'imdb_id']:
            imdb_id = root.findtext(tag)
            if imdb_id:
                imdb_id = imdb_id.strip()
                if imdb_id.startswith("tt"):
                    ids.append(imdb_id)
                elif imdb_id.isdigit():
                    ids.append("tt%s" % imdb_id)

        for uid in root.findall('uniqueid'):
            uid_value = uid.text.strip() if uid.text else ''
            if uid_value:
                if uid.attrib.get('type', '').lower() == 'imdb' and not uid_value.startswith('tt'):
                    uid_value = "tt%s" % uid_value
                ids.append(uid_value)

        for tag in ['tmdbid', 'tvdbid', 'rottentomatoesid']:
            value = root.findtext(tag)
            if value and value.strip().isdigit():
                ids.append(value.strip())

        season = root.findtext('season')
        episode = root.findtext('episode')
        season = int(season) if season and season.strip().isdigit() else None
        episode = int(episode) if episode and episode.strip().isdigit() else None

        return (ids if ids else None), season, episode
    except:
        pass
    return None, None, None

# Grabs currently playing media. 
def get_now_playing():
    player = xbmc.Player()

    if player.isPlayingAudio():
        artist = xbmc.getInfoLabel('MusicPlayer.Artist')
        title = xbmc.getInfoLabel('MusicPlayer.Title')
        if artist and title:
            return artist + ' - ' + title, None, None

    elif player.isPlayingVideo():
        file_path = player.getPlayingFile()
        if file_path:
            base, _ = os.path.splitext(file_path)
            nfo_path = base + ".nfo"
            ids, season, episode = extract_ids_from_nfo(nfo_path)
            if ids:
                # If TVDB id is found, return with season/episode if present
                for idval in ids:
                    if idval.isdigit():
                        return idval, season, episode  # TVDB series id, season, episode
                    elif idval.startswith("tt"):
                        return idval, None, None  # IMDb id, no season/episode
                return ids[0], None, None  # fallback

            title = xbmc.getInfoLabel("VideoPlayer.Title")
            if title and title.strip():
                return title.strip(), None, None

            return os.path.splitext(os.path.basename(file_path))[0], None, None

    return None, None, None

def main():
    last_sent = (None, None, None)
    server_ip = discover_server()
    if not server_ip:
        print('No xbdStats server found. Exiting.')
        return

    if dashboard_enabled and dashboard_type:
        send_to_server(dashboard_type, None, None, "dashboard", server_ip)
    else:
        send_to_server("", None, None, None, server_ip)

    try:
        while True:
            idval, season, episode = get_now_playing()
            current_sent = (idval, season, episode)
            if idval and idval.strip() and current_sent != last_sent:
                media_type = "music" if is_music_playing() else "video"
                send_to_server(idval, season, episode, media_type, server_ip)
                last_sent = current_sent
            elif (not idval or not idval.strip()) and last_sent != (None, None, None):
                # If DASHBOARD_ENABLED is true, send DASHBOARD_TYPE instead of clearing
                if dashboard_enabled and dashboard_type:
                    send_to_server(dashboard_type, None, None, "dashboard", server_ip)
                else:
                    send_to_server("", None, None, None, server_ip)
                last_sent = (None, None, None)
            time.sleep(5)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
