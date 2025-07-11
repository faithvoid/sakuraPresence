# sakuraRPC
Discord Rich Presence for all network-capable retro consoles. Includes multi-media support!

## Features:
- PS1/PS2/PS3/Xbox/Xbox 360/Wii/Wii U support!
- Super modular and straightforward, can be adapted to any console that can send TCP/UDP packets!

## How to Use (as a user):
- Download the latest sakuraRPC release .zip
- Go into the "consoles" folder and copy over your sakuraRPC launcher of choice to your system
- Copy "sakuraRPC.py" anywhere you'll remember it
- Run "sakuraRPC.py" (make sure Discord Rich Presence is enabled!)
- Run the sakuraRPC launcher from your console and you should see your game and title ID automagically appear!

## How to Use (as a developer):
If you're developing an add-on using this server as a base, making a console-specific plugin is super easy! You just need to send a TCP/UDP packet with contents like the following 
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
### Console Dashboard
```{"dashboard": true, "id": "X360_DASH"}``` Xbox 360 Dashboard 


replacing the console name with the console you'd like to use, and the ID with the ID pulled from the game (the matching XBMC4Xbox script pulls this information from the .XBE files, but YMMV depending on console).

To make an entry for a console's dashboard, you'll want to send a packet like so:
``` {"dashboard": true, "id": "X360_DASH"} ``` 

For multi-media, you'll want to send a packet like so:
``` {"music": true, "id": "Artist - Title"} ``` 
or
``` {"video": true, "id": "Title"} ``` 

## Roadmap
- [ ] Integrating proper XLink Kai arena support into every XLink-capable system
- [x] PS1/PS2/PS3/PSP support
- [x] Xbox / Xbox 360 support
- [x] Wii / Wii U support
- [ ] Dreamcast support
- [ ] Gamecube support
- [ ] DS / 3DS support
- [ ] Switch support
- [ ] Tkinter-based GUI?
- [ ] Find better sources for cover art

## Credits:
- Mobcat + Milenko - Original "xbdStats" server that this is based off of.
- xlenore - PS1/PS2 cover art sources
- TVDB
- TMDB
- Insignia Team
- XLink Kai Team
- Many more coming soon!
