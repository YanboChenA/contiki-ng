#include "contiki.h"
#include "net/ipv6/simple-udp.h"
#include "net/mac/tsch/tsch.h"
#include "net/mac/tsch/tsch-schedule.h"
#include "lib/random.h"
#include "sys/node-id.h"
#include <string.h>

#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO

#define UDP_PORT	8765
#define SEND_INTERVAL		  (60 * CLOCK_SECOND)

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


static void send_sensor_data(uip_ipaddr_t *dest_ipaddr, struct etimer *timer) {
    static int sensor_index = 0; // Initialize the sensor index
    static SensorData current_data; // Static to keep track of the current sensor data across function calls
    SensorData next_data; // Initialize the next data struct

    static uint32_t seqnum = 0;
    char sensor_id = 'A' + (node_id - 1); // Set node id

    // Logic to get current and next sensor data
    if (sensor_index == 0 || current_data.timestamp == 0) {
        current_data = get_sensor_data(sensor_id, sensor_index);
    }
    next_data = get_sensor_data(sensor_id, sensor_index + 1);

    if (next_data.timestamp != 0) {
        // Calculate the time interval between two readings and adjust the timer
        clock_time_t next_interval = (next_data.timestamp - current_data.timestamp) * CLOCK_SECOND;
        etimer_set(timer, next_interval);
        current_data = next_data;
        sensor_index++;
    } else {
        // Reset the sensor index and current data if no next data
        sensor_index = 0;
        memset(&current_data, 0, sizeof(current_data));
        etimer_set(timer, SEND_INTERVAL);
    }

    // Send the sensor data
    seqnum++;
    LOG_INFO("Sending to ");
    LOG_INFO_6ADDR(dest_ipaddr);
    LOG_INFO_(", seqnum %" PRIu32 ", Sensor ID: %c\n", seqnum, sensor_id);
    
    simple_udp_sendto(&udp_conn, &current_data, sizeof(current_data), dest_ipaddr);
}

PROCESS_THREAD(node_process, ev, data) {
    static struct etimer sensor_timer;
    static struct etimer schedule_timer;

    static uip_ipaddr_t dest_ipaddr;

    PROCESS_BEGIN();

    simple_udp_register(&udp_conn, UDP_PORT, NULL, UDP_PORT, rx_callback);
    
    if (node_id == 1) { 
        NETSTACK_ROUTING.root_start();
    }
    NETSTACK_MAC.on();

    etimer_set(&sensor_timer, random_rand() % SEND_INTERVAL);
    etimer_set(&schedule_timer, random_rand() % SEND_INTERVAL);

    while(1) {
        PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&sensor_timer));

        if(NETSTACK_ROUTING.node_is_reachable() && NETSTACK_ROUTING.get_root_ipaddr(&dest_ipaddr)) {
            send_sensor_data(&dest_ipaddr, &sensor_timer);
        } else {
            // Reset the timer if the network is not reachable or the root IP address cannot be obtained
            etimer_set(&sensor_timer, SEND_INTERVAL);
        }

        // Periodically print the scheduling table
        if(etimer_expired(&schedule_timer)) {
            tsch_schedule_print();
            etimer_reset(&schedule_timer);
        }
    }

    PROCESS_END();
}