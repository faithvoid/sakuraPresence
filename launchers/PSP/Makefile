TARGET = sakuraPresence
OBJS = main.o
BUILD_PRX = 1

CFLAGS = -O2 -G0 -Wall -D_PSP_FW_VERSION=600

EXTRA_TARGETS = EBOOT.PBP

PSP_EBOOT_TITLE = sakuraPresence
PSP_HEAP_SIZE = 1024*1024
PSP_EBOOT_CATEGORY = MG

PSPSDK = $(shell psp-config --pspsdk-path)
include $(PSPSDK)/lib/build.mak
