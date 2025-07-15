#include <pspkernel.h>
#include <pspdebug.h>
#include <pspnet.h>
#include <pspnet_inet.h>
#include <pspnet_apctl.h>
#include <pspiofilemgr.h>
#include <pspctrl.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <psputility.h>

PSP_MODULE_INFO("sakuraPresence", 0, 1, 0);
PSP_MAIN_THREAD_ATTR(THREAD_ATTR_USER | THREAD_ATTR_VFPU);

#define printf pspDebugScreenPrintf
#define PARAM_SFO_OFFSET 0x28

typedef struct {
    char name[64];
} FileEntry;

#define MAX_FILES 128

FileEntry fileList[MAX_FILES];
int fileCount = 0;

int setupNetwork() {
    sceUtilityLoadNetModule(PSP_NET_MODULE_COMMON);
    sceUtilityLoadNetModule(PSP_NET_MODULE_INET);
    sceUtilityLoadNetModule(PSP_NET_MODULE_HTTP);

    sceNetInit(128 * 1024, 42, 2 * 1024, 42, 2 * 1024);
    sceNetInetInit();
    sceNetApctlInit(0x1800, 48);

    int stateLast = -1;
    int err = sceNetApctlConnect(1);
    if (err != 0) return err;

    while (1) {
        int state;
        sceNetApctlGetState(&state);
        if (state != stateLast) {
            printf("Net state: %d\n", state);
            stateLast = state;
        }
        if (state == 4) break;
        sceKernelDelayThread(1000000);
    }
    return 0;
}


unsigned int resolveIP(const char* ip) {
    unsigned int b1, b2, b3, b4;
    sscanf(ip, "%u.%u.%u.%u", &b1, &b2, &b3, &b4);
    return (b1 << 24) | (b2 << 16) | (b3 << 8) | b4;
}

int sendJson(const char* id) {
    const char* server_ip = "192.168.1.110";
    int port = 1102;
    int sock = sceNetInetSocket(AF_INET, SOCK_STREAM, 0);

    if (sock < 0) {
        printf("Failed to create socket\n");
        return -1;
    }

    struct sockaddr_in server;
    server.sin_len = sizeof(server);
    server.sin_family = AF_INET;
    server.sin_port = htons(port);
    server.sin_addr.s_addr = htonl(resolveIP(server_ip));

    if (sceNetInetConnect(sock, (struct sockaddr*)&server, sizeof(server)) < 0) {
        printf("Connection failed.\n");
        sceNetInetClose(sock);
        return -1;
    }

    char buffer[128];
    snprintf(buffer, sizeof(buffer), "{\"psp\": true, \"id\": \"%s\"}", id);
    sceNetInetSend(sock, buffer, strlen(buffer), 0);
    sceNetInetClose(sock);
    printf("Sent JSON: %s\n", buffer);
    return 0;
}

typedef struct {
    char magic[4];
    uint32_t version;
    uint32_t keyTableStart;
    uint32_t dataTableStart;
    uint32_t tableEntries;
} __attribute__((packed)) PSFHeader;

typedef struct {
    uint16_t keyOffset;
    uint8_t  alignment;
    uint8_t  entryType;
    uint32_t valueSize;
    uint32_t totalSize;
    uint32_t dataOffset;
} __attribute__((packed)) PSFEntry;

int getTitleID(const char* pbp_path, char* outID, size_t outIDSize) {
    FILE* f = fopen(pbp_path, "rb");
    if (!f) return -1;

    fseek(f, PARAM_SFO_OFFSET, SEEK_SET);
    uint32_t paramOffset = 0;
    fread(&paramOffset, sizeof(paramOffset), 1, f);
    if (paramOffset == 0) {
        fclose(f);
        return -2; 
    }

    fseek(f, paramOffset, SEEK_SET);

    PSFHeader hdr;
    fread(&hdr, sizeof(hdr), 1, f);

    if (memcmp(hdr.magic, "PSF\0", 4) != 0) {
        fclose(f);
        return -3; 
    }

    long keyTablePos = paramOffset + hdr.keyTableStart;
    long dataTablePos = paramOffset + hdr.dataTableStart;

    for (uint32_t i = 0; i < hdr.tableEntries; i++) {
        PSFEntry entry;
        fread(&entry, sizeof(entry), 1, f);

        long curPos = ftell(f);

        fseek(f, keyTablePos + entry.keyOffset, SEEK_SET);
        char key[64];
        if (fgets(key, sizeof(key), f) == NULL) {
            fclose(f);
            return -4;
        }

        size_t len = strlen(key);
        if (len > 0 && (key[len - 1] == '\n' || key[len - 1] == '\r')) {
            key[len - 1] = '\0';
        }

        if (strcmp(key, "TITLE_ID") == 0) {
            fseek(f, dataTablePos + entry.dataOffset, SEEK_SET);
            if (entry.entryType == 2) {
                if (entry.valueSize >= outIDSize) {
                    fclose(f);
                    return -5;
                }
                fread(outID, 1, entry.valueSize, f);
                outID[entry.valueSize - 1] = '\0';
                fclose(f);
                return 0;
            }
        }

        fseek(f, curPos, SEEK_SET);
    }

    fclose(f);
    return -6;
}

int getTitleIDFromPBP(const char* pbp_path, char* outID, size_t outIDSize) {
    FILE* f = fopen(pbp_path, "rb");
    if (!f) return -1;

    uint32_t dataOffsetLE = 0;
    fseek(f, 0x20, SEEK_SET);
    fread(&dataOffsetLE, sizeof(dataOffsetLE), 1, f);

    uint32_t dataOffset = (dataOffsetLE & 0xFF) |
                          ((dataOffsetLE >> 8) & 0xFF) << 8 |
                          ((dataOffsetLE >> 16) & 0xFF) << 16 |
                          ((dataOffsetLE >> 24) & 0xFF) << 24;
  
    if (fseek(f, dataOffset + 0x120, SEEK_SET) != 0) {
        fclose(f);
        return -2;
    }

    if (fread(outID, 1, 8, f) != 8) {
        fclose(f);
        return -3;
    }
    outID[8] = '\0';

    fclose(f);
    return 0;
}

void scanDirectory(const char* path) {
    fileCount = 0;

    SceIoDirent dir;
    int dfd = sceIoDopen(path);
    if (dfd < 0) {
        printf("Failed to open directory: %s\n", path);
        return;
    }

    while (sceIoDread(dfd, &dir) > 0 && fileCount < MAX_FILES) {
        if (dir.d_name[0] == '.') continue;

        strncpy(fileList[fileCount].name, dir.d_name, sizeof(fileList[fileCount].name) - 1);
        fileList[fileCount].name[sizeof(fileList[fileCount].name) - 1] = '\0';
        fileCount++;
    }
    sceIoDclose(dfd);
}

int main(int argc, char* argv[]) {
    pspDebugScreenInit();

    int res = setupNetwork();
    if (res != 0) {
        printf("Network setup failed: %08X\n", res);
        sceKernelSleepThread();
        return 1;
    }

    const char* basePath = "ms0:/PSP/GAME/";
    scanDirectory(basePath);

    if (fileCount == 0) {
        printf("No files found in %s\n", basePath);
        sendJson(id);
        sceKernelSleepThread();
        return 0;
    }

    int selected = 0;
    SceCtrlData pad;

    while (1) {
        pspDebugScreenClear();
        printf("Select a file (LEFT/RIGHT):\n\n");

        int start = (selected / 5) * 5;
        int end = start + 5;
        if (end > fileCount) end = fileCount;

        for (int i = start; i < end; i++) {
            if (i == selected) {
                printf("-> %s\n", fileList[i].name);
            } else {
                printf("   %s\n", fileList[i].name);
            }
        }

        printf("\nPress CROSS to scan and send title ID.\n");
        printf("Press CIRCLE to exit.\n");

        sceCtrlPeekBufferPositive(&pad, 1);
        if (pad.Buttons & PSP_CTRL_RIGHT) {
            selected++;
            if (selected >= fileCount) selected = 0;
            sceKernelDelayThread(150000);
        } else if (pad.Buttons & PSP_CTRL_LEFT) {
            selected--;
            if (selected < 0) selected = fileCount - 1;
            sceKernelDelayThread(150000);
        } else if (pad.Buttons & PSP_CTRL_CROSS) {
            char fullPath[256];
            snprintf(fullPath, sizeof(fullPath), "%s%s", basePath, fileList[selected].name);

            char id[16] = {0};
            int ret = getTitleIDFromPBP(fullPath, id, sizeof(id));
            if (ret != 0) {
                ret = getTitleID(fullPath, id, sizeof(id));
            }

            if (ret == 0) {
                printf("Title ID: %s\n", id);
                sendJson(id);
            } else {
                printf("No valid Title ID found.\n");
                sendJson("UCUS98612");
            }
            sceKernelDelayThread(2000000);
        } else if (pad.Buttons & PSP_CTRL_CIRCLE) {
            break;
        }

        sceKernelDelayThread(100000);
    }

    return 0;
}
