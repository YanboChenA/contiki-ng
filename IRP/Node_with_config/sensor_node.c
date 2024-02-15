#include "contiki.h"
#include "net/ipv6/simple-udp.h"
#include "net/mac/tsch/tsch.h"
#include "net/mac/tsch/tsch-schedule.h"
#include "lib/random.h"
#include "sys/node-id.h"
#include <string.h>
#include <stdlib.h>

#include "events.h" 

#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO

#define UDP_PORT	8765
// #define SEND_INTERVAL		  (60 * CLOCK_SECOND)

#define PACKET_SIZE 100 // Default data size
#define SEND_INTERVAL (10 * CLOCK_SECOND) // Default send interval

static struct simple_udp_connection udp_conn;

static void 
rx_callback( struct simple_udp_connection *c,
                  const uip_ipaddr_t *sender_addr,
                  uint16_t sender_port,
                  const uip_ipaddr_t *receiver_addr,
                  uint16_t receiver_port,
                  const uint8_t *data,
                  uint16_t datalen)
{
    uint32_t seqnum;
    if(datalen >= sizeof(seqnum)) {
        memcpy(&seqnum, data, sizeof(seqnum));

        LOG_INFO("Received from ");
        LOG_INFO_6ADDR(sender_addr);
        LOG_INFO_(", seqnum %" PRIu32 "\n", seqnum);
    }
}


static void send_data(uip_ipaddr_t *dest_ipaddr, struct etimer *timer, uint32_t packet_size) {
    static uint32_t seqnum =0;

    // uint8_t payload[packet_size] = {0}; // Example payload data

    uint8_t payload[packet_size];
    memset(payload, 0, sizeof(payload));

    seqnum++;
    LOG_INFO("Sending to ");
    LOG_INFO_6ADDR(dest_ipaddr);
    LOG_INFO_(", seqnum %" PRIu32 "\n", seqnum);

    simple_udp_sendto(&udp_conn, payload, packet_size, dest_ipaddr);
}


PROCESS(sensor_node_process, "Sensor Node Process");
AUTOSTART_PROCESSES(&sensor_node_process);

PROCESS_THREAD(sensor_node_process, ev, data) {
    static struct etimer send_timer;
    static struct etimer event_timer;
    static clock_time_t next_interval;

    uint32_t si = SEND_INTERVAL;
    uint32_t ps = PACKET_SIZE;

    static uip_ipaddr_t dest_ipaddr;

    int event_index = 0;
    // set initial event_timer
    etimer_set(&event_timer, event_list[event_index].time);
    event_index++;
    
    PROCESS_BEGIN();
    
    simple_udp_register(&udp_conn, UDP_PORT, NULL, UDP_PORT, rx_callback);

    if (node_id == 1) { 
        NETSTACK_ROUTING.root_start();
    }
    NETSTACK_MAC.on();

    while(1) {
        //set a switch to wait the event timer or send timer:
        if(etimer_expired(&event_timer)){
            //check the node id 
            if(node_id == event_list[event_index].node_id){
                // Check if the node should go offline
                if(event_list[event_index].event_type == EVENT_FAILURE){
                    NETSTACK_MAC.off(); // Turn off the MAC layer to simulate node going offline
                } 
                else if(event_list[event_index].event_type == EVENT_RECOVERY){
                    NETSTACK_MAC.on(); // Make sure the MAC layer is on
                }
                else if(event_list[event_index].event_type == EVENT_LOAD_VARIATION){
                    si = event_list[event_index].target_send_interval * CLOCK_SECOND;
                    ps = event_list[event_index].target_packet_size;
                }
                event_index++;
                if (event_index < event_list_size){
                    next_interval = (event_list[event_index].time - event_list[event_index-1].time) * CLOCK_SECOND;
                    etimer_set(&event_timer, next_interval);
                }
            }
        }
            
        if (etimer_expired(&send_timer)) {
            if(NETSTACK_ROUTING.node_is_reachable() && NETSTACK_ROUTING.get_root_ipaddr(&dest_ipaddr)) {
                send_data(&dest_ipaddr, &send_timer,ps);
            }
            etimer_set(&send_timer, si);
        }
    }

    PROCESS_END();
}