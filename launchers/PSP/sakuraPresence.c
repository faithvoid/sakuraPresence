#include <pspkernel.h>
#include <pspdebug.h>
#include <pspnet.h>
#include <pspnet_inet.h>
#include <pspnet_apctl.h>
#include <pspwlan.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <psputility_netmodules.h>
#include <pspiofilemgr.h>
#include <pspumd.h>
#include <psputility.h>
#include <pspctrl.h>
#include <psploadexec.h>
#include <stdint.h>
#include <pspmoduleinfo.h>

PSP_MODULE_INFO("sakuraPresence", 0, 1, 0);
PSP_MAIN_THREAD_ATTR(THREAD_ATTR_USER | THREAD_ATTR_VFPU);
PSP_HEAP_SIZE_KB(8*1024);

#define SERVER_IP "192.168.1.110"
#define SERVER_PORT 1102
#define MAX_PATH_LENGTH 256
#define MAX_FILES 1024

typedef struct {
    char name[MAX_PATH_LENGTH];
    int isDir;
} FileEntry;

FileEntry fileList[MAX_FILES];
int fileCount = 0;
char currentPath[MAX_PATH_LENGTH] = "ms0:/";

void cleanupNetwork() {
    sceNetApctlDisconnect();
    sceNetApctlTerm();
    sceNetInetTerm();
    sceNetTerm();
    sceUtilityUnloadNetModule(PSP_NET_MODULE_INET);
    sceUtilityUnloadNetModule(PSP_NET_MODULE_COMMON);
}

int connectToNetwork() {
    int err;

    pspDebugScreenPrintf("Loading net modules...\n");
    err = sceUtilityLoadNetModule(PSP_NET_MODULE_COMMON);
    if (err < 0) {
        pspDebugScreenPrintf("Load PSP_NET_MODULE_COMMON failed: 0x%08X\n", err);
        return err;
    }

    err = sceUtilityLoadNetModule(PSP_NET_MODULE_INET);
    if (err < 0) {
        pspDebugScreenPrintf("Load PSP_NET_MODULE_INET failed: 0x%08X\n", err);
        return err;
    }

    err = sceNetInit(128 * 1024, 0x30, 0x1000, 0x30, 0x1000);
    if (err != 0) {
        pspDebugScreenPrintf("sceNetInit failed: 0x%08X\n", err);
        return err;
    }

    err = sceNetInetInit();
    if (err != 0) {
        pspDebugScreenPrintf("sceNetInetInit failed: 0x%08X\n", err);
        return err;
    }

    err = sceNetApctlInit(0x1800, 48);
    if (err != 0) {
        pspDebugScreenPrintf("sceNetApctlInit failed: 0x%08X\n", err);
        return err;
    }

    err = sceNetApctlConnect(1);
    if (err != 0) {
        pspDebugScreenPrintf("sceNetApctlConnect() failed: 0x%08X\n", err);
        return err;
    }

    int lastState = -1;
    while (1) {
        int state;
        sceNetApctlGetState(&state);
        if (state != lastState) {
            pspDebugScreenPrintf("Net state: %d\n", state);
            lastState = state;
        }
        if (state == 4) break;
        sceKernelDelayThread(500000);
    }

    pspDebugScreenPrintf("Network connected!\n");
    return 0;
}

int sendPacket(const char* gameID) {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        pspDebugScreenPrintf("Failed to create socket\n");
        return -1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(SERVER_PORT);
    addr.sin_addr.s_addr = inet_addr(SERVER_IP);

    char packet[256];
    snprintf(packet, sizeof(packet), "{\"psp\": true, \"id\": \"%s\"}", gameID);

    int sent = sendto(sock, packet, strlen(packet), 0, (struct sockaddr *)&addr, sizeof(addr));
    if (sent < 0) {
        pspDebugScreenPrintf("Failed to send packet\n");
        close(sock);
        return -1;
    }

    pspDebugScreenPrintf("Packet sent: %s\n", packet);
    close(sock);
    return 0;
}

int sendDashPacket(const char* gameID) {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        pspDebugScreenPrintf("Failed to create socket\n");
        return -1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(SERVER_PORT);
    addr.sin_addr.s_addr = inet_addr(SERVER_IP);

    char packet[256];
    snprintf(packet, sizeof(packet), "{\"dashboard\": true, \"id\": \"%s\"}", gameID);

    int sent = sendto(sock, packet, strlen(packet), 0, (struct sockaddr *)&addr, sizeof(addr));
    if (sent < 0) {
        pspDebugScreenPrintf("Failed to send packet\n");
        close(sock);
        return -1;
    }

    pspDebugScreenPrintf("Packet sent: %s\n", packet);
    close(sock);
    return 0;
}

void scanDirectory(const char* path) {
    fileCount = 0;

    SceUID dir = sceIoDopen(path);
    if (dir < 0) {
        pspDebugScreenPrintf("Failed to open directory: %s\n", path);
        return;
    }

    SceIoDirent entry;
    memset(&entry, 0, sizeof(entry));

    while (sceIoDread(dir, &entry) > 0 && fileCount < MAX_FILES) {
        if (strcmp(entry.d_name, ".") != 0 && strcmp(entry.d_name, "..") != 0) {
            strncpy(fileList[fileCount].name, entry.d_name, MAX_PATH_LENGTH);
            fileList[fileCount].isDir = FIO_S_ISDIR(entry.d_stat.st_mode);
            fileCount++;
        }
    }

    sceIoDclose(dir);
}

static uint16_t readLE16(const unsigned char* data) {
    return (uint16_t)data[0] | ((uint16_t)data[1] << 8);
}

static uint32_t readLE32(const unsigned char* data) {
    return (uint32_t)data[0] | 
          ((uint32_t)data[1] << 8) | 
          ((uint32_t)data[2] << 16) | 
          ((uint32_t)data[3] << 24);
}

int readFileToBuffer(const char* path, unsigned char** buffer, size_t* size) {
    SceUID fd = sceIoOpen(path, PSP_O_RDONLY, 0777);
    if (fd < 0) {
        pspDebugScreenPrintf("Failed to open file: %s\n", path);
        return -1;
    }
    
    *size = sceIoLseek(fd, 0, PSP_SEEK_END);
    sceIoLseek(fd, 0, PSP_SEEK_SET);
    
    *buffer = malloc(*size);
    if (!*buffer) {
        sceIoClose(fd);
        return -1;
    }
    
    int read = sceIoRead(fd, *buffer, *size);
    sceIoClose(fd);
    
    if (read != *size) {
        free(*buffer);
        return -1;
    }
    
    return 0;
}

int extractGameIDFromPBP(const char* path, char* gameID, size_t gameIDSize) {
    unsigned char* pbpData = NULL;
    size_t pbpSize = 0;

    if (readFileToBuffer(path, &pbpData, &pbpSize) < 0) {
        pspDebugScreenPrintf("Failed to read PBP file\n");
        return -1;
    }

    if (pbpSize < 0x28 || memcmp(pbpData, "\0PBP", 4) != 0) {
        pspDebugScreenPrintf("Invalid or corrupt PBP header\n");
        free(pbpData);
        return -1;
    }

    uint32_t sfoOffset = readLE32(pbpData + 0x08);
    if (sfoOffset + 20 > pbpSize) {
        pspDebugScreenPrintf("SFO offset out of range\n");
        free(pbpData);
        return -1;
    }

    const unsigned char* sfo = pbpData + sfoOffset;

    if (readLE32(sfo) != 0x46535000) {
        pspDebugScreenPrintf("Invalid SFO magic\n");
        free(pbpData);
        return -1;
    }

    uint32_t keyTableOff = readLE32(sfo + 8);
    uint32_t dataTableOff = readLE32(sfo + 12);
    uint32_t entryCount   = readLE32(sfo + 16);
    const unsigned char* entries = sfo + 20;

    for (uint32_t i = 0; i < entryCount; i++) {
        const unsigned char* entry = entries + i * 16;

        uint16_t keyOff    = readLE16(entry + 0);
        uint16_t fmt       = readLE16(entry + 2);
        uint32_t len       = readLE32(entry + 4);
        uint32_t dataOff   = readLE32(entry + 12); 

        const char* key = (const char*)(sfo + keyTableOff + keyOff);

        if (strcmp(key, "DISC_ID") == 0 || strcmp(key, "TITLE_ID") == 0) {
            const char* value = (const char*)(sfo + dataTableOff + dataOff);

            pspDebugScreenPrintf("Raw ID data (%d bytes): ", len);
            for (uint32_t j = 0; j < len && j < 16; j++) {
                pspDebugScreenPrintf("%02X ", (unsigned char)value[j]);
            }
            pspDebugScreenPrintf("\n");

            size_t actualLen = 0;
            while (actualLen < len && value[actualLen] != '\0') {
                actualLen++;
            }

            if (gameIDSize == 0) {
                pspDebugScreenPrintf("Invalid gameID buffer size\n");
                free(pbpData);
                return -1;
            }

            size_t copyLen = (actualLen < gameIDSize - 1) ? actualLen : gameIDSize - 1;
            memcpy(gameID, value, copyLen);
            gameID[copyLen] = '\0';

            pspDebugScreenPrintf("Found %s: '%s' (length: %d)\n", key, gameID, actualLen);
            
            free(pbpData);
            return 0;
        }
    }

    pspDebugScreenPrintf("DISC_ID or TITLE_ID not found\n");
    free(pbpData);
    return -1;
}


void displayFileBrowser(int* selected) {
    pspDebugScreenClear();
    pspDebugScreenPrintf("Current path: %s\n\n", currentPath);

    for (int i = 0; i < fileCount; i++) {
        if (i == *selected) {
            pspDebugScreenPrintf("> ");
        } else {
            pspDebugScreenPrintf("  ");
        }

        if (fileList[i].isDir) {
            pspDebugScreenPrintf("[%s]\n", fileList[i].name);
        } else {
            pspDebugScreenPrintf("%s\n", fileList[i].name);
        }
    }
}

void launchGame(const char* path, const char* gameID) {
    pspDebugScreenPrintf("Preparing to launch %s...\n", path);

    cleanupNetwork();

    sceKernelDelayThread(1000000);

    struct SceKernelLoadExecParam param;
    memset(&param, 0, sizeof(param));
    param.size = sizeof(param);
    param.args = 0;
    param.argp = NULL;
    param.key = NULL;

    pspDebugScreenPrintf("Launching %s...\n", path);
    int ret = sceKernelLoadExec(path, &param);
    if (ret < 0) {
        pspDebugScreenPrintf("Failed to launch game! Error: 0x%08X\n", ret);
        sceKernelDelayThread(3000000);
        connectToNetwork();
    }
}


int main(int argc, char *argv[]) {
    pspDebugScreenInit();
    pspDebugScreenPrintf("Starting sakuraPresence...\n");

    unsigned int oldButtons = 0;
    unsigned int holdStart = 0;
    int showHelp = 0;

    if (connectToNetwork() == 0) {
        sendDashPacket("PSP");
    }

    sceCtrlSetSamplingCycle(0);
    sceCtrlSetSamplingMode(PSP_CTRL_MODE_ANALOG);

    int selected = 0;
    int lastSelected = -1;
    int dirty = 1;
    scanDirectory(currentPath);

    while (1) {
        if (dirty || selected != lastSelected) {
            displayFileBrowser(&selected);
            if (showHelp) {
                pspDebugScreenPrintf("\nControls:\n");
                pspDebugScreenPrintf("X - Open/Launch\n");
                pspDebugScreenPrintf("O - Go Back\n");
                pspDebugScreenPrintf("START - Exit\n");
                pspDebugScreenPrintf("SELECT - Toggle Help\n");
            }
            lastSelected = selected;
            dirty = 0;
        }

        SceCtrlData pad;
        sceCtrlReadBufferPositive(&pad, 1);

        unsigned int newPresses = pad.Buttons & ~oldButtons;

        if (pad.Buttons & PSP_CTRL_START) {
            holdStart++;
            if (holdStart > 60) {
                sceKernelExitGame();
            }
        } else {
            holdStart = 0;
        }

        if (newPresses & PSP_CTRL_UP) {
            selected--;
            if (selected < 0) selected = fileCount - 1;
            dirty = 1;
            sceKernelDelayThread(150000);
        }
        else if (newPresses & PSP_CTRL_DOWN) {
            selected++;
            if (selected >= fileCount) selected = 0;
            dirty = 1;
            sceKernelDelayThread(150000);
        }
        else if (newPresses & PSP_CTRL_START) {
            pspDebugScreenPrintf("\nChecking network connection...\n");
            int state;
            sceNetApctlGetState(&state);
            pspDebugScreenPrintf("Network state: %d\n", state);
            sceKernelDelayThread(1000000);
            dirty = 1;
        }
        else if (newPresses & PSP_CTRL_SELECT) {
            showHelp = !showHelp;
            dirty = 1;
            sceKernelDelayThread(200000);
        }
        else if (newPresses & PSP_CTRL_CROSS) {
            char newPath[MAX_PATH_LENGTH];
            snprintf(newPath, sizeof(newPath), "%s%s", currentPath, fileList[selected].name);

            if (fileList[selected].isDir) {
                strcat(newPath, "/");
                strncpy(currentPath, newPath, MAX_PATH_LENGTH);
                scanDirectory(currentPath);
                selected = 0;
                dirty = 1;
            } else {
                const char* ext = strrchr(fileList[selected].name, '.');
                if (ext) {
                    if (strcasecmp(ext, ".pbp") == 0) {
                        char gameID[16];
                        pspDebugScreenPrintf("\nExtracting Title ID...\n");
                        
                        if (extractGameIDFromPBP(newPath, gameID, sizeof(gameID)) == 0) {
                            pspDebugScreenPrintf("Title ID: %s\n", gameID);
                            launchGame(newPath, gameID);
                        } else {
                            pspDebugScreenPrintf("Failed to extract Title ID\n");
                            sceKernelDelayThread(2000000);
                        }
                        dirty = 1;
                    } else {
                        pspDebugScreenPrintf("\nUnsupported file type: %s\n", ext);
                        sceKernelDelayThread(1000000);
                        dirty = 1;
                    }
                } else {
                    pspDebugScreenPrintf("\nNo file extension\n");
                    sceKernelDelayThread(1000000);
                    dirty = 1;
                }
            }
        }
        else if (newPresses & PSP_CTRL_CIRCLE) {
            if (strcmp(currentPath, "ms0:/") != 0) {
                char* lastSlash = strrchr(currentPath, '/');
                if (lastSlash) {
                    if (lastSlash == currentPath + strlen(currentPath) - 1) {
                        *lastSlash = '\0';
                        lastSlash = strrchr(currentPath, '/');
                    }
                    if (lastSlash) {
                        *lastSlash = '\0';
                        strcat(currentPath, "/");
                    } else {
                        strcpy(currentPath, "ms0:/");
                    }
                }
                scanDirectory(currentPath);
                selected = 0;
                dirty = 1;
            }
            sceKernelDelayThread(150000);
        }

        oldButtons = pad.Buttons;
        sceKernelDelayThread(16000);
    }

    cleanupNetwork();
    sceKernelExitGame();
    return 0;
}
