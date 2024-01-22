#include "contiki.h"
#include "net/ipv6/simple-udp.h"
#include "net/mac/tsch/tsch.h"
#include "lib/random.h"
#include "sys/node-id.h"

#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO

#define UDP_PORT	8765
#define SEND_INTERVAL		  (30 * CLOCK_SECOND)

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

    PROCESS_BEGIN();

    /* Initialize UDP Connection for root node or sub node */
    simple_udp_register(&udp_conn, UDP_PORT, NULL,
                UDP_PORT, rx_callback);

    etimer_set(&periodic_timer, random_rand() % SEND_INTERVAL);
    if (node_id == 1) { 
      NETSTACK_ROUTING.root_start();
    }
    NETSTACK_MAC.on();

    while(1) {
        PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&periodic_timer));

        if(NETSTACK_ROUTING.node_is_reachable() &&
            NETSTACK_ROUTING.get_root_ipaddr(&dest_ipaddr)) {
            /*For the root node Send message to the network root node */
            seqnum++;
            LOG_INFO("Send to ");
            LOG_INFO_6ADDR(&dest_ipaddr);
            LOG_INFO_(", seqnum %" PRIu32 "\n", seqnum);

            simple_udp_sendto(&udp_conn, &seqnum, sizeof(seqnum), &dest_ipaddr);
        }

    etimer_set(&periodic_timer, SEND_INTERVAL);
    }
    PROCESS_END();
}