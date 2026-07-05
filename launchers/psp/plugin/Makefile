TARGET = sakuraPresencePRX
OBJS = sakuraPresencePRX.o

CFLAGS = -O2 -G0 -Wall
LDFLAGS =

LIBS = -lpspnet -lpspnet_apctl -lpsputility -lpspumd -lpspwlan

PSPSDK = $(shell psp-config --pspsdk-path)
include $(PSPSDK)/lib/build_prx.mak
