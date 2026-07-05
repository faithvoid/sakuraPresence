#include <pspkernel.h>
#include <pspdebug.h>
#include <pspnet.h>
#include <pspnet_apctl.h>
#include <pspnet_inet.h>
#include <pspwlan.h>
#include <psputility_netmodules.h>
#include <pspctrl.h>
#include <pspdisplay.h>
#include <pspumd.h>
#include <pspge.h>
#include <string.h>
#include <arpa/inet.h>
#include <netinet/in.h>

PSP_MODULE_INFO("sakuraPresencePRX", PSP_MODULE_USER, 1, 1);

#define SERVER_IP "192.168.1.110"
#define SERVER_PORT 1102
#define LOG_FILE "ms0:/log.txt"
#define PRESENCE_FILE "ms0:/presence.txt"


void presence_ip(const char* msg) {
    SceUID fd = sceIoOpen(PRESENCE_FILE, PSP_O_RDONLY, 0666);
}


void logline(const char* msg) {
    SceUID fd = sceIoOpen(LOG_FILE, PSP_O_WRONLY | PSP_O_CREAT | PSP_O_APPEND, 0666);
    if (fd >= 0) {
        sceIoWrite(fd, msg, strlen(msg));
        sceIoWrite(fd, "\n", 1);
        sceIoClose(fd);
    }
}

void logHex(const char* label, int value) {
    char hexChars[] = "0123456789ABCDEF";
    char buf[64];
    int pos = 0;

    while (*label && pos < 48)
        buf[pos++] = *label++;

    buf[pos++] = ':';
    buf[pos++] = ' ';
    buf[pos++] = '0';
    buf[pos++] = 'x';

    for (int i = 7; i >= 0; i--)
        buf[pos++] = hexChars[(value >> (i * 4)) & 0xF];

    buf[pos++] = '\0';
    logline(buf);
}

void logInt(const char* label, int value) {
    char buf[64];
    int pos = 0;

    while (*label && pos < 48)
        buf[pos++] = *label++;

    buf[pos++] = ':';
    buf[pos++] = ' ';

    char digits[12];
    int i = 0;

    if (value == 0) {
        digits[i++] = '0';
    } else {
        while (value > 0 && i < 11) {
            digits[i++] = '0' + (value % 10);
            value /= 10;
        }
    }

    while (i > 0 && pos < 63)
        buf[pos++] = digits[--i];

    buf[pos++] = '\0';
    logline(buf);
}

int ensureNetworkReady() {
    int err;

    logline("Loading net modules...");

    err = sceUtilityLoadNetModule(PSP_NET_MODULE_COMMON);
    if (err < 0 && err != 0x80110802) {
        logHex("Load COMMON failed", err);
        return err;
    }

    err = sceUtilityLoadNetModule(PSP_NET_MODULE_INET);
    if (err < 0 && err != 0x80110802) {
        logHex("Load INET failed", err);
        return err;
    }

    if ((err = sceNetInit(128 * 1024, 0x30, 0x1000, 0x30, 0x1000)) < 0) {
        logHex("sceNetInit failed", err);
        return err;
    }

    if ((err = sceNetInetInit()) < 0) {
        logHex("sceNetInetInit failed", err);
        return err;
    }

    if ((err = sceNetApctlInit(0x1800, 48)) < 0) {
        logHex("sceNetApctlInit failed", err);
        return err;
    }

    if ((err = sceNetApctlConnect(1)) < 0) {
        logHex("sceNetApctlConnect failed", err);
        return err;
    }

    int lastState = -1;
    int retries = 0;
    while (retries++ < 100) {
        int state;
        sceNetApctlGetState(&state);
        if (state != lastState) {
            lastState = state;
            logInt("Net state", state);
        }
        if (state == 4) break;
        sceKernelDelayThread(100000); // 100ms
    }

    if (lastState != 4) {
        logline("Network connect timeout");
        return -1;
    }

    logline("Network connected!");
    return 0;
}

int extractGameID(char* gameID, size_t gameIDSize) {
    logline("Opening PARAM.SFO...");
    SceUID fd = sceIoOpen("disc0:/PSP_GAME/PARAM.SFO", PSP_O_RDONLY, 0777);
    if (fd < 0) {
        logline("Failed to open PARAM.SFO");
        return -1;
    }

    int size = sceIoLseek(fd, 0, PSP_SEEK_END);
    sceIoLseek(fd, 0, PSP_SEEK_SET);
    if (size <= 0 || size > 2048) {
        sceIoClose(fd);
        logline("Invalid PARAM.SFO size");
        return -1;
    }

    static unsigned char buffer[2048];
    if (sceIoRead(fd, buffer, size) != size) {
        sceIoClose(fd);
        logline("Failed to read PARAM.SFO");
        return -1;
    }
    sceIoClose(fd);

    uint32_t keyTableOff = *(uint32_t *)(buffer + 8);
    uint32_t dataTableOff = *(uint32_t *)(buffer + 12);
    uint32_t entryCount = *(uint32_t *)(buffer + 16);
    unsigned char* entries = buffer + 20;

    for (uint32_t i = 0; i < entryCount; i++) {
        unsigned char* entry = entries + i * 16;
        uint16_t keyOff = *(uint16_t *)(entry + 0);
        uint32_t dataOff = *(uint32_t *)(entry + 12);
        const char* key = (const char*)(buffer + keyTableOff + keyOff);
        if (strcmp(key, "DISC_ID") == 0 || strcmp(key, "TITLE_ID") == 0) {
            const char* value = (const char*)(buffer + dataTableOff + dataOff);
            strncpy(gameID, value, gameIDSize - 1);
            gameID[gameIDSize - 1] = '\0';
            logline("Game ID found");
            return 0;
        }
    }

    logline("Game ID not found");
    return -1;
}

void sendGameID(const char* gameID) {
    int sock = sceNetInetSocket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        logline("Socket creation failed");
        return;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(SERVER_PORT);
    addr.sin_addr.s_addr = inet_addr(SERVER_IP);

    char packet[128];
    strcpy(packet, "{\"psp\":true,\"id\":\"");
    strcat(packet, gameID);
    strcat(packet, "\"}");

    int sent = sceNetInetSendto(sock, packet, strlen(packet), 0, (struct sockaddr*)&addr, sizeof(addr));
    if (sent > 0)
        logline("Game ID sent");
    else
        logline("sendto failed");

    sceNetInetClose(sock);
}


void cleanupNetwork() {
    logline("Cleaning up network");
    sceNetApctlDisconnect();
    sceNetApctlTerm();
    sceNetInetTerm();
    sceNetTerm();
    sceUtilityUnloadNetModule(PSP_NET_MODULE_INET);
    sceUtilityUnloadNetModule(PSP_NET_MODULE_COMMON);
}

int sendThread(SceSize args, void *argp) {
    logline("Thread started");

    sceKernelDelayThread(3 * 1000000); // Wait 3 seconds to allow game to load

    if (ensureNetworkReady() == 0) {
        char gameID[32] = {0};
        if (extractGameID(gameID, sizeof(gameID)) == 0) {
            sendGameID(gameID);
        } else {
            logline("extractGameID failed");
        }
        cleanupNetwork();
    } else {
        logline("Network init failed");
    }

    logline("Thread done");
    sceKernelExitDeleteThread(0);
}

int module_start(SceSize args, void *argp) {
    logline("module_start");
    int thid = sceKernelCreateThread("sakuraPresenceThread", sendThread, 0x30, 0x20000, PSP_THREAD_ATTR_USER, NULL);
    if (thid >= 0) {
        sceKernelStartThread(thid, 0, NULL);
    } else {
        logline("Thread creation failed");
    }
    return 0;
}

int module_stop(SceSize args, void *argp) {
    logline("module_stop");
    return 0;
}

void* getModuleInfo(void)
{
	return (void *) &module_info;
}
