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
PSP_HEAP_SIZE_KB(12*1024);

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

int sendPacket(const char* titleID) {
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
    snprintf(packet, sizeof(packet), "{\"psp\": true, \"id\": \"%s\"}", titleID);

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

int sendDashPacket(const char* titleID) {
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
    snprintf(packet, sizeof(packet), "{\"dashboard\": true, \"id\": \"%s\"}", titleID);

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

int extractTitleIDFromPBP(const char* path, char* titleID, size_t titleIDSize) {
    unsigned char* pbpData = NULL;
    size_t pbpSize = 0;
    
    if (readFileToBuffer(path, &pbpData, &pbpSize) < 0) {
        pspDebugScreenPrintf("Failed to read PBP file\n");
        return -1;
    }
    
    if (pbpSize < 0x28) {
        pspDebugScreenPrintf("PBP file too small (%lu bytes)\n", pbpSize);
        free(pbpData);
        return -1;
    }
    
    uint32_t sfoOffset = readLE32(pbpData + 0x8);
    uint32_t sfoSize = readLE32(pbpData + 0xC) - sfoOffset;
    
    if (sfoOffset >= pbpSize || sfoOffset + sfoSize > pbpSize) {
        pspDebugScreenPrintf("Invalid SFO section in PBP (offset: 0x%08X, size: 0x%08X)\n", 
                            sfoOffset, sfoSize);
        free(pbpData);
        return -1;
    }
    
    const unsigned char* sfoData = pbpData + sfoOffset;
    
    if (readLE32(sfoData) != 0x46535000) { 
        pspDebugScreenPrintf("Invalid SFO magic\n");
        free(pbpData);
        return -1;
    }
    
    uint32_t version = readLE32(sfoData + 4);
    uint32_t keyTableOffset = readLE32(sfoData + 8);
    uint32_t dataTableOffset = readLE32(sfoData + 12);
    uint32_t entryCount = readLE32(sfoData + 16);
    
    if (version != 0x0101 || entryCount > 100 || 
        keyTableOffset >= sfoSize || dataTableOffset >= sfoSize) {
        pspDebugScreenPrintf("Invalid SFO structure\n");
        free(pbpData);
        return -1;
    }
    
    const unsigned char* entries = sfoData + 20;
    int found = 0;
    
    for (uint32_t i = 0; i < entryCount && !found; i++) {
        uint16_t keyOffset = readLE16(entries + (i * 16));
        uint16_t dataFormat = entries[(i * 16) + 2];
        uint32_t dataLength = entries[(i * 16) + 4];
        uint32_t dataOffset = readLE32(entries + (i * 16) + 8);
        
        const char* key = (const char*)(sfoData + keyTableOffset + keyOffset);
        
        if (strcmp(key, "DISC_ID") == 0) {
            const char* data = (const char*)(sfoData + dataTableOffset + dataOffset);
            
            size_t copyLen = (dataLength < titleIDSize - 1) ? dataLength : titleIDSize - 1;
            strncpy(titleID, data, copyLen);
            titleID[copyLen] = '\0';
            
            found = 1;
        }
    }
    
    free(pbpData);
    
    if (!found) {
        pspDebugScreenPrintf("TITLE_ID not found in PARAM.SFO\n");
        return -1;
    }
    
    return 0;
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

void launchGame(const char* path, const char* titleID) {
    pspDebugScreenPrintf("Preparing to launch %s...\n", path);

    if (sendPacket(titleID) < 0) {
        pspDebugScreenPrintf("Failed to send title ID\n");
    }

    cleanupNetwork();

    sceKernelDelayThread(1000000);

    struct SceKernelLoadExecParam param;
    memset(&param, 0, sizeof(param));
    param.size = sizeof(param);
    param.args = strlen(path) + 1;
    param.argp = (void*)path;
    param.key = "game";

    pspDebugScreenPrintf("Launching %s...\n", path);
    sceKernelLoadExec(path, &param);

    pspDebugScreenPrintf("Failed to launch game!\n");
    sceKernelDelayThread(3000000);

    connectToNetwork();
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
                        char titleID[10] = {0};
                        pspDebugScreenPrintf("\nExtracting Title ID...\n");
                        
                        if (extractTitleIDFromPBP(newPath, titleID, sizeof(titleID)) == 0) {
                            pspDebugScreenPrintf("Title ID: %s\n", titleID);
                            launchGame(newPath, titleID);
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
