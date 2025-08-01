# 🌸sakuraPresence
Discord Rich Presence for all network-capable retro consoles (8th generation and prior). Includes multi-media support!

![](screenshots/ps1.png)![](screenshots/ps2.png)
![](screenshots/ps3.png)![](screenshots/ps4.png)
![](screenshots/psp.png)![](screenshots/vita.png)
![](screenshots/gc.png)![](screenshots/wii.png)
![](screenshots/wiiu.png)![](screenshots/switch.png)
![](screenshots/ds.png)![](screenshots/3ds.png)
![](screenshots/xbox.png)![](screenshots/360.png)
![](screenshots/dreamcast.png)


## Features:
- Support for multiple consoles! If you can send a network packet, you can send a presence!
- Super modular and straightforward, can be adapted to any console or emulator with networking!
- Integrated XLink Kai / Insignia / RPCN multiplayer statistics for games where that information is available, as well as automatic XLink Kai arena detection for supported titles!
- Homebrew support! (currently only for Xbox + Xbox 360)

## Supported Systems:
### Sony
- [x] Playstation (server-side)
- [x] Playstation 2 (server-side) (includes XLink Kai support)
- [x] Playstation 3 (server-side) (includes XLink Kai & RPCN support)
- [x] Playstation 4 (server-side) (includes XLink Kai support)
- [x] [Playstation Portable](https://github.com/faithvoid/sakuraPresencePSP) (server + client-side) (includes XLink Kai support)
- [x] Playstation Vita (server-side) (includes XLink Kai support)
### Microsoft
- [x] [Xbox](https://github.com/OfficialTeamUIX/Xbox-Discord-Rich-Presence) (includes XLink Kai & Insignia support) (128mb recommended for media presence) (server + client-side)
- [x] [Xbox 360](https://github.com/OfficialTeamUIX/Xbox-Discord-Rich-Presence) (includes XLink Kai support) (server-side)
### Nintendo
- [x] Nintendo Gamecube (server-side) (includes XLink Kai support)
- [x] Nintendo Wii (server-side) (includes XLink Kai support)
- [x] Nintendo Wii U (server-side) (includes XLink Kai support)
- [x] Nintendo DS (server-side)
- [x] Nintendo 3DS (server-side)
- [x] Nintendo Switch (server-side) (includes XLink Kai support)

## Planned Systems:
- [ ] Dreamcast (almost finished, just need to finish cover art directory)
- [ ] Emulators plug-ins(?)
- [ ] Xbox One (using Dbox API, unsure of how to get cover art just yet)

## How to Use (as a user):
- Download the latest sakuraPresence release .zip
- Go into the "consoles" folder and copy over your sakuraPresence launcher of choice to your system
- Copy "sakuraPresence.py" and "config.cfg" anywhere you'll remember it
- Set up your various API keys, user profiles and PS3/360 IP addresses and polling frequency in config.cfg
- Run "sakuraPresence.py" (make sure Discord Rich Presence is enabled!)
- Run the sakuraPresence launcher from your console and you should see your game and title ID automagically appear!

## How to Use (as a developer):
If you're developing a client using this server as a base, making a console-specific plugin or game launcher is super easy! You just need to send a TCP/UDP packet with a console ID as a true/false value and the titleID as a string. Examples below:

## Sony
### Playstation
```{"ps1": true, "id": "SLUS-00662"}``` Parasite Eve Disc 1
### Playstation 2
```{"ps2": true, "id": "SLUS-20765"}``` Resident Evil Outbreak 
### Playstation 3
```{"ps3": true, "id": "BLUS30094"}``` Haze
### Playstation 4
```{"ps3": true, "id": "CUSA07559"}``` .hack//G.U Last Recode
### Playstation Portable
```{"psp": true, "id": "UCUS98711"}``` Patapon
```{"psp": true, "md5": "9a7870fbb2597d28af2b7ef83f66a6f8"}```  Quake III Arena (homebrew, MD5)
### Playstation Vita
```{"psp": true, "id": "PCSD00035"}``` Gravity Rush

## Microsoft
### Xbox
```{"xbox": true, "id": "4D530064"}```  Halo 2

```{"xbox": true, "id": "fff3faad"}```  Quake III Arena (homebrew, title ID)

```{"xbox": true, "md5": "9a7870fbb2597d28af2b7ef83f66a6f8"}```  Quake III Arena (homebrew, MD5, recommended as most homebrew doesn't have a valid title ID)

### Xbox 360
```{"xbox360": true, "id": "4D5307E6"}``` Halo 3 

```{"xbox360": true, "id": "fff3faad"}```  Quake III Arena (homebrew, title ID)

```{"xbox360": true, "md5": "9a7870fbb2597d28af2b7ef83f66a6f8"}```  Quake III Arena (homebrew, MD5, recommended as most homebrew doesn't have a valid title ID)

## Nintendo
### Gamecube
```{"gc": true, "id": "GZLE01"}``` The Legend of Zelda: Wind Waker
### Wii
```{"wii": true, "id": "RMCE01"}``` Mario Kart Wii
### Wii U
```{"wiiu": true, "id": "ABAE"}``` Mario Party 10
### DS
```{"ds": true, "id": "AMHJ"}``` Metroid Prime Hunters
### 3DS
```{"3ds": true, "id": "0004000000033500"}``` Super Mario Party 10
### Switch
```{"switch": true, "id": "0100152000022000"}``` Mario Kart 8 Deluxe

## Sega
### Dreamcast
```{"dc": true, "id": "51000"}``` Sonic Adventure (USA)

## Etc.
### Console Dashboard
```{"dashboard": true, "id": "XBOX_DASH"}``` Xbox Dashboard (can call any platform listed above for dashboard idling mode)

### Music
``` {"music": true, "id": "Orbital - Halcyon & On & On"} ``` Orbital - Halcyon & On & On (MusicBrainz)
``` {"music": true, "id": "OrbitalHalcyonAndOnAndOn.mp3"} ``` OrbitalHalcyonAndOnAndOn.mp3 (local file)

Sending the correct artist and song information will automatically search via MusicBrainz and fetch the associated information automatically! If this data can't be found (usually in the ID3 metadata), it'll fall back to the name of the file.

### Videos
``` {"video": true, "id": "tt0133093"} ``` The Matrix (IMDB ID) 
``` {"video": true, "id": "The Matrix (1994).avi"} ``` The Matrix (local file) 
``` {"video": true, "id": "268999", "season":1, "episode":1} ``` Daria S01E01 (TVDB ID)
Resolving videos via TMDB/TVDB will grab cover art, episode/film information, plot synopsis, and more! This can easily be fetched by storing an .NFO generated by Jellyfin/Plex/Emby/etc. containing these values alongside the video file you're watching, and fetching that .NFO file when the media is accessed. (sakuraMedia for XBMC does this!)

For an example of how a game plugin or launcher can work, please look at the Python files in system/xbox (either mediapresence.py or gamepresence.py) to see how it parses game information (this implementation scans the .XBE file for the title ID, similar practices may be possible on other consoles, and if not, MD5 scanning or disc-based title reading reading is an option, please let me know if this is something you need for your presence project and I'll implement it server-side!)

## Roadmap
- [ ] Playstation - Serial port support
- [ ] Playstation Portable - USB support
- [ ] Xbox / Xbox 360 homebrew support (need to finish database)
- [ ] PS3 homebrew support
- [ ] PSP homebrew support (possibly not though, a lot of homebrew just reports back as Loco Roco).
- [ ] Dreamcast support
- [ ] Tkinter-based GUI? (include start/stop server button, "clear presence" button)
- [ ] Server-side console toggles
- [ ] Manual system/game selection via the UI
- [ ] Wiimmfi support (not possible at the moment due to no external API + CloudFlare protection)
- [ ] Better commenting and documentation for developers
- [ ] Optimization (this is already at 1.8k lines of code because a ton of functionality was duplicated to save time during testing. Also uses approx. 52MB of RAM, which can definitely be improved by loading files on-demand instead of all at once.)

## FAQ:
### Will this run on a Raspberry Pi?
Technically yes, technically no. There isn't an official ARM port of Discord, but there are unofficial ports you can use (or attempt to run it via WINE on a newer Pi), but unauthorized third-client usage may result in your Discord account being terminated, so we don't recommend anything except the official Discord client. sakuraPresence also currently uses 52MB of RAM, which may be an issue on older Pi models. 
### Will you support (current-gen console here)?
![](https://en.meming.world/images/en/thumb/1/1d/Creating_Bugs_Bunny%27s_%22No%22.jpg/300px-Creating_Bugs_Bunny%27s_%22No%22.jpg)
### "Will this come to XYZ older-generation console?"
I'll implement server-side support for almost anything, but if you don't see a client on the roadmap, someone else will have to make it!
### "XYZ title ID is missing!"
Open up an issue on GitHub with the missing title ID and I'll fix it right away!
### How can I help?
We need client developers/maintainers, cover art repositories, and people to scan their console homebrew for title IDs and MD5 IDs using the utilities provided in the "utilities" folder to add to the Homebrew database!

## Credits:
- Mobcat + Milenko - Original "xbdStats" server that this is based off of. This wouldn't be possible without their hard work!
- Mega - PS3 testing and WebMAN info grabbing support.
- xlenore - PS1/PS2 cover art sources
- OGXbox team - Insignia / XLink Kai statistics
- RPSC3 team - RCPN stats
- TVDB - TV episode information
- TMDB - Movie information
- MusicBrainz + CoverArtArchive - Music information
- Insignia Team 
- XLink Kai Team
- GameTDB - 3DS/Switch/Wii/Wii U title databases and cover art
- aldostools - PSP / PS3 title databases + cover art
- OrbisPatches - PS4 cover art
- LutzPS - Console icons + homebrew title icons
- Many more coming soon!
