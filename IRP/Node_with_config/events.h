#ifndef EVENTS_H_
#define EVENTS_H_

#include "contiki.h"

typedef enum {
    EVENT_FAILURE,
    EVENT_RECOVERY,
    EVENT_LOAD_VARIATION
} event_type_t;

typedef struct {
    clock_time_t time;
    event_type_t event_type;
    int target_send_interval;
    int target_packet_size;
    int node_id;
} node_event_t;

int event_list_size = 10;

node_event_t event_list[] = {
    {.time = 100, .event_type = EVENT_LOAD_VARIATION, .target_send_interval = 15, .target_packet_size = 15, .node_id = -1},
    {.time = 200, .event_type = EVENT_LOAD_VARIATION, .target_send_interval = 5, .target_packet_size = 15, .node_id = -1},
    {.time = 300, .event_type = EVENT_LOAD_VARIATION, .target_send_interval = 20, .target_packet_size = 15, .node_id = 1},
    {.time = 400, .event_type = EVENT_LOAD_VARIATION, .target_send_interval = 5, .target_packet_size = 15, .node_id = 1},
    {.time = 500, .event_type = EVENT_LOAD_VARIATION, .target_send_interval = 25, .target_packet_size = 15, .node_id = 2},
    {.time = 600, .event_type = EVENT_LOAD_VARIATION, .target_send_interval = 5, .target_packet_size = 15, .node_id = 2},
    {.time = 800, .event_type = EVENT_FAILURE, .target_send_interval = 5, .target_packet_size = 15, .node_id = 3},
    {.time = 1000, .event_type = EVENT_RECOVERY, .target_send_interval = 5, .target_packet_size = 15, .node_id = 3},
    {.time = 2000, .event_type = EVENT_FAILURE, .target_send_interval = 5, .target_packet_size = 15, .node_id = 2},
    {.time = 2100, .event_type = EVENT_RECOVERY, .target_send_interval = 5, .target_packet_size = 15, .node_id = 2},
};

#endif /* EVENTS_H_ */

