CONTIKI_PROJECT = root_node sensor_node
all: $(CONTIKI_PROJECT)

PLATFORMS_ONLY = cooja

CONTIKI=../..

# force Security from command line
MAKE_WITH_SECURITY ?= 0

MAKE_MAC = MAKE_MAC_TSCH

include $(CONTIKI)/Makefile.dir-variables
MODULES += $(CONTIKI_NG_SERVICES_DIR)/shell

ifeq ($(MAKE_WITH_SECURITY),1)
CFLAGS += -DWITH_SECURITY=1
endif

MODULES_REL += $(CONTIKI)/utils/sensor_data_io
MODULES_REL += $(CONTIKI)/data/temp_data

include $(CONTIKI)/Makefile.include