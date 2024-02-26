#include "contiki.h"
#include "net/ipv6/uip.h"
#include "net/ipv6/simple-udp.h"
#include "net/ipv6/uip-ds6.h"
#include "net/mac/tsch/tsch.h"
#include "net/mac/tsch/tsch-schedule.h"
#include "lib/random.h"
#include "sys/node-id.h"
#include <string.h>
#include <stdlib.h>

#include "net/packetbuf.h"
#include "sys/energest.h"

// #include "net/routing/rpl-lite/rpl.h"
// #include "net/rpl/rpl-private.h"

#include "events.h" 

#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO

#define UDP_PORT	8765

#define PACKET_SIZE 100 // Default data size
#define SEND_INTERVAL (10 * CLOCK_SECOND) // Default send interval
#define LOG_INTERVAL (30 * CLOCK_SECOND) // Default log interval


static struct simple_udp_connection udp_conn;



static void 
rx_callback( struct simple_udp_connection *c,
                  const uip_ipaddr_t *sender_addr,
                  uint16_t sender_port,
                  const uip_ipaddr_t *receiver_addr,
                  uint16_t receiver_port,
                  const uint8_t *data,
                  uint16_t datalen){   
    int16_t rssi = packetbuf_attr(PACKETBUF_ATTR_RSSI);
    uint8_t lqi = packetbuf_attr(PACKETBUF_ATTR_LINK_QUALITY);

    static uint32_t seqnum;
    // if(datalen >= sizeof(seqnum)) {
    memcpy(&seqnum, data, sizeof(seqnum));

    LOG_INFO("APP: Received from ");
    LOG_INFO_6ADDR(sender_addr);
    LOG_INFO_(", seqnum %" PRIu32 "", seqnum);
    LOG_INFO_(", RSSI: %d, LQI: %u\n",rssi, lqi);
}


static void send_data(uip_ipaddr_t *dest_ipaddr, uint32_t packet_size) {
    static uint32_t seqnum = 0;

    uint8_t payload[packet_size];
    for (int i = 0; i < packet_size; i++) {
        payload[i] = rand() % 256;
    }
    memcpy(payload, &seqnum, sizeof(seqnum));

    LOG_INFO("APP: Sending to ");
    LOG_INFO_6ADDR(dest_ipaddr);
    LOG_INFO_(", seqnum %" PRIu32 "\n", seqnum);

    seqnum++;

    simple_udp_sendto(&udp_conn, payload, packet_size, dest_ipaddr);
}


PROCESS(sensor_node_process, "Sensor Node Process");
AUTOSTART_PROCESSES(&sensor_node_process);

PROCESS_THREAD(sensor_node_process, ev, data) {
    static struct etimer send_timer;
    static struct etimer event_timer;
    static struct etimer log_timer;

    static clock_time_t next_interval;
    static bool send_enable = true;

    static uint32_t si = SEND_INTERVAL;
    static uint32_t ps = PACKET_SIZE;

    static uip_ipaddr_t dest_ipaddr;
    static int event_index = 0;

    static radio_value_t incorrect_pan_id = 0xFFFF; // Incorrect PAN ID for leave network
    static radio_value_t correct_pan_id;


    static uint32_t log_index = 0;

    PROCESS_BEGIN();

    simple_udp_register(&udp_conn, UDP_PORT, NULL, UDP_PORT, rx_callback);

    if (node_id == 1) { 
        uip_ipaddr_t root_ipaddr;
        NETSTACK_ROUTING.root_start();



        NETSTACK_ROUTING.get_root_ipaddr(&root_ipaddr);
        LOG_INFO("Node %d started as root, root ip address: ", node_id);
        LOG_INFO_6ADDR(&root_ipaddr);
        LOG_INFO_("\n");
    }
    NETSTACK_MAC.on();


    etimer_set(&send_timer, random_rand() % si);
    etimer_set(&event_timer, event_list[0].time * CLOCK_SECOND);
    etimer_set(&log_timer, LOG_INTERVAL);

    while(1) {
        PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&send_timer));
        if(NETSTACK_ROUTING.node_is_reachable() && NETSTACK_ROUTING.get_root_ipaddr(&dest_ipaddr)){
            if(send_enable == true){
                send_data(&dest_ipaddr, ps);
            }
            
            etimer_set(&send_timer, si);
        }

        if(etimer_expired(&event_timer) && event_index < event_list_size){
            // Check the node id 
            if (node_id == event_list[event_index].node_id || event_list[event_index].node_id == -1) {
                LOG_INFO("Event timer expired, event index: %d, event type: %d, current time: %lu\n", event_index, event_list[event_index].event_type, clock_time());
                // Check if the node should go offline
                if (event_list[event_index].event_type == EVENT_FAILURE) {
                    NETSTACK_RADIO.get_value(RADIO_PARAM_PAN_ID, &correct_pan_id);
                    send_enable = false;
                    NETSTACK_RADIO.set_value(RADIO_PARAM_PAN_ID, incorrect_pan_id);
                    LOG_INFO("Node %d went offline\n", node_id);
                } 
                else if (event_list[event_index].event_type == EVENT_RECOVERY) {
                    NETSTACK_MAC.on(); // Make sure the MAC layer is on
                    // tsch_associate();
                    send_enable = true;
                    NETSTACK_RADIO.set_value(RADIO_PARAM_PAN_ID, correct_pan_id);
                    LOG_INFO("Node %d recovered\n", node_id);
                }
                else if (event_list[event_index].event_type == EVENT_LOAD_VARIATION) {
                    si = event_list[event_index].target_send_interval * CLOCK_SECOND;
                    ps = event_list[event_index].target_packet_size;
                    LOG_INFO("Node %d changed send interval to %" PRIu32 " and packet size to %" PRIu32 "\n", node_id, si, ps);
                }
            }
            event_index++;
            // LOG_INFO("event_index: %d\n", event_index);
            if (event_index < event_list_size){
                next_interval = (event_list[event_index].time - event_list[event_index-1].time);
                etimer_set(&event_timer, next_interval * CLOCK_SECOND);
            }
        }

        if(etimer_expired(&log_timer)){
            energest_flush();
            LOG_INFO("Energest: Index %d CPU %lu LPM %lu TX %lu RX %lu Total_time %lu\n",
                            log_index,
                            energest_type_time(ENERGEST_TYPE_CPU),
                            energest_type_time(ENERGEST_TYPE_LPM),
                            energest_type_time(ENERGEST_TYPE_TRANSMIT),
                            energest_type_time(ENERGEST_TYPE_LISTEN),
                            ENERGEST_GET_TOTAL_TIME());
            etimer_set(&log_timer, LOG_INTERVAL);
            log_index++;
        }
    }
    PROCESS_END();
}

