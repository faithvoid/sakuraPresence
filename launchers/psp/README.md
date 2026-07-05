# sakuraPresencePSP
Discord Rich Presence proof of concept application for the Playstation Portable.

![](screenshots/SAKU01860_00002.jpg)
![](screenshots/SAKU01860_00003.jpg)

## Working:
- Fetching title ID from .PBP file
- Sending title ID from .PBP as a packet to a hardcoded IP address over network via the first available connection
- Launching .PBP (PPSSPP only)

## Not Working:
- Launching .PBP on real hardware (sceLoadExec only launches .PBPs when it has kernel access, which this application doesn't by default, but PPSSPP ignores that and launches PBPs anyway)
- UMD support (implemented but untested, doesn't seem to work in PPSSPP)
- ISO/CSO support

# sakuraPresencePRX (plugin version)
PRX module version. Currently partially working, it launches after the user launches a game from the XMB and correctly sends presence data via the PARAM.SFO on the UMD (virtual or not) but then crashes the system around the main menu of most games. 

## Working:
- Initializing network state after game launch
- Sending presence data after network connect
- Logging to memory card
## Not Working:
- Progressing past the main menu in any game (it seems there's some sort of resource issue, as games will successfully load their intro videos, but will crash shortly after module cleanup). 


## Roadmap:
- [ ] Move server IP and port to .cfg file
- [ ] Get .PRX plugin to stop crashing in-game
