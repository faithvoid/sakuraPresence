# ![](https://cdn.discordapp.com/app-assets/1379734520508579960/1393481542910611476.png) sakuraPresence
Discord Rich Presence for all network-capable retro consoles. Includes multi-media support!
## Features:
- Support for multiple retro consoles! If you can send a network packet, you can send a presence!
- Super modular and straightforward, can be adapted to any console or emulator with networking!
- Integrated XLink / Insignia / RPCN multiplayer statistics for games where that information is available!
- Homebrew support! (currently only for Xbox + Xbox 360)

## Supported Systems:
- Playstation
- Playstation 2
- Playstation 3
- Playstation Portable
- [Xbox](https://github.com/OfficialTeamUIX/Xbox-Discord-Rich-Presence) (128mb recommended for media presence)
- [Xbox 360](https://github.com/OfficialTeamUIX/Xbox-Discord-Rich-Presence)
- Nintendo Wii

## Planned Systems:
- Dreamcast
- Gamecube
- Switch
- Wii U
- DS + 3DS

## How to Use (as a user):
- Download the latest sakuraPresence release .zip
- Go into the "consoles" folder and copy over your sakuraPresence launcher of choice to your system
- Copy "sakuraPresence.py" anywhere you'll remember it
- Run "sakuraPresence.py" (make sure Discord Rich Presence is enabled!)
- Run the sakuraPresence launcher from your console and you should see your game and title ID automagically appear!

## How to Use (as a developer):
If you're developing an add-on using this server as a base, making a console-specific plugin or game launcher is super easy! You just need to send a TCP/UDP packet with titleID of the game you've launched like the following:

### Playstation
```{"ps1": true, "id": "SLUS-00662"}``` Parasite Eve Disc 1
### Playstation 2
```{"ps2": true, "id": "SLUS-20765"}``` Resident Evil Outbreak 
### Playstation 3
```{"ps3": true, "id": "BLUS30094"}``` Haze
### Playstation Portable
```{"psp": true, "id": "UCUS98711"}``` Patapon
### Xbox
```{"xbox": true, "id": "4D530064"}```  Halo 2
### Xbox 360
```{"xbox360": true, "id": "4D5307E6"}``` Halo 3 
### Gamecube
```{"gc": true, "id": "DOL-GZLE-USA"}``` The Legend of Zelda: Wind Waker
### Wii
```{"wii": true, "id": "RMCE01"}``` Mario Kart Wii
### Wii U
```{"wiiu": true, "id": "WUP-P-ABAE"}``` Super Mario Party 10
### DS
```{"ds": true, "id": "AMHJ"}``` Metroid Prime Hunters
### 3DS
```{"3ds": true, "id": "0004000000033500"}``` Super Mario Party 10
### Switch
```{"switch": true, "id": "0100152000022000"}``` Mario Kart 8 Deluxe
### Dreamcast
```{"dc": true, "id": "51000"}``` Sonic Adventure (USA)
### Console Dashboard
```{"dashboard": true, "id": "XBOX_DASH"}``` Xbox Dashboard (can call any platform listed above for dashboard idling mode)

### Music
``` {"music": true, "id": "Artist - Title"} ``` 
This will resolve your tracks via MusicBrainz!

### Videos
``` {"video": true, "id": "Title"} ``` 
This will resolve your video files via TMDB/TVDB to grab cover art, episode/film information, plot synopsis, and more!

For an example of how a game plugin or launcher can work, please look at the Python files in system/xbox (either mediapresence.py or gamepresence.py) to see how it parses game information (this implementation scans the .XBE file for the title ID, similar practices may be possible on other consoles, and if not, MD5 scanning or disc-based title reading reading is an option, please let me know if this is something you need for your presence project and I'll implement it server-side!)

## Roadmap
- [x] PS1/PS2/PS3/PSP support
- [x] Xbox / Xbox 360 support
- [ ] Xbox / Xbox 360 homebrew support (need to finish database)
- [x] Wii / Wii U support
- [ ] Dreamcast support
- [ ] Gamecube support
- [ ] DS / 3DS support
- [ ] Switch support
- [ ] Tkinter-based GUI?
- [ ] Server-side console toggles
- [ ] Find better sources for cover art
- [ ] Integrating proper XLink Kai arena support into every XLink-capable system
- [x] RPCN support
- [ ] Wiimmfi support (not possible at the moment due to no external API + CloudFlare protection)
- [ ] Better commenting and documentation for developers
- [ ] Optimization (this is already at 1.5k lines of code because a ton of functionality was duplicated to save time during testing)

## Credits:
- Mobcat + Milenko - Original "xbdStats" server that this is based off of. This wouldn't be possible without their hard work!
- xlenore - PS1/PS2 cover art sources
- OGXbox team - Insignia / XLink Kai statistics
- RPSC3 team - RCPN stats
- TVDB - TV episode information
- TMDB - Movie information
- MusicBrainz + CoverArtArchive - Music information
- Insignia Team 
- XLink Kai Team
- Many more coming soon!
