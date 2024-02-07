#include "contiki.h"
#include "net/ipv6/simple-udp.h"
#include "net/mac/tsch/tsch.h"
#include "lib/random.h"
#include "sys/node-id.h"
#include <string.h>

#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO

#define UDP_PORT	8765
#define SEND_INTERVAL		  (30 * CLOCK_SECOND)

#include "sensor_utils.h" // Include the sensor_utils.h file form ../../utils folder
#include "sensor_data.h" // Include the sensor data file from ../../data/sensor_data folder

PROCESS(node_process, "TSCH Node");
AUTOSTART_PROCESSES(&node_process);

/*
 * This node is for simple udp to transmit data to root node
 * This node include both root node and sub node.
 * The root node is the coordinator of the network, and receive data from sub node.
 * The callback function of root node is to print the information of received message 
 * from sub node, and send response to sub node.
 * The sub node is the node which send data to root node periodically.
 * The callback function of sub node is to print the information of received message from response.
 */
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

PROCESS_THREAD(node_process, ev, data)
{
    static struct etimer periodic_timer;
    static uip_ipaddr_t dest_ipaddr;
    static uint32_t seqnum;

    static int sensor_index = 0; // Initialize the sensor index
    SensorData current_data; // Initialize the current data struct
    SensorData next_data; // Initialize the next data struct
    memset(&current_data, 0, sizeof(current_data));
    memset(&next_data, 0, sizeof(next_data));


    PROCESS_BEGIN();

    /* Initialize UDP Connection for root node or sub node */
    simple_udp_register(&udp_conn, UDP_PORT, NULL,
                UDP_PORT, rx_callback);

    etimer_set(&periodic_timer, random_rand() % SEND_INTERVAL);
    if (node_id == 1) { 
      NETSTACK_ROUTING.root_start();
    }
    NETSTACK_MAC.on();

    /* Set node id and son node id */
    char sensor_id = 'A' + (node_id - 1);

    while(1) {
        PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&periodic_timer));

        if(NETSTACK_ROUTING.node_is_reachable() &&
            NETSTACK_ROUTING.get_root_ipaddr(&dest_ipaddr)) {
                
            // Get the current data for the given sensor ID and its occurrence index
            // If current_data is not exist, get the first data of the sensor
            if (sensor_index == 0 || current_data.timestamp == 0) {
                current_data = get_sensor_data(sensor_id, sensor_index);
            }

            // Get the next data for the given sensor ID and its occurrence index
            next_data = get_sensor_data(sensor_id, sensor_index + 1);

            if (next_data.timestamp != 0) {
                // Get the time interval between two consecutive readings of the same sensor
                unsigned long next_interval = next_data.timestamp - current_data.timestamp;
                etimer_set(&periodic_timer, next_interval);
                current_data = next_data;
                sensor_index++;
            } else {
                // If the next data is not exist, reset the sensor index and current data
                etimer_set(&periodic_timer, SEND_INTERVAL);
                sensor_index = 0;
                memset(&current_data, 0, sizeof(current_data));
            }

            /*For the root node Send message to the network root node */
            seqnum++;
            LOG_INFO("Send to ");
            LOG_INFO_6ADDR(&dest_ipaddr);
            LOG_INFO_(", seqnum %" PRIu32 "\n", seqnum);
            
            simple_udp_sendto(&udp_conn, &current_data, sizeof(current_data), &dest_ipaddr);

            // LOG_INFO_("Sensor ID: %c, Data Size: %d\n", sensor_id, sizeof(current_data));

        }

    etimer_set(&periodic_timer, SEND_INTERVAL);
    }
    PROCESS_END();
}