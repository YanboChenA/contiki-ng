#include "contiki.h"
#include "sys/node-id.h"
#include "sys/log.h"
#include "net/ipv6/uip-ds6-route.h"
#include "net/ipv6/uip-sr.h"
#include "net/mac/tsch/tsch.h"
#include "net/routing/routing.h"
#include "random.h"
#include "net/netstack.h"
#include "net/ipv6/simple-udp.h"
#include <stdint.h>
#include <inttypes.h>

#define DEBUG DEBUG_PRINT
#include "net/ipv6/uip-debug.h"

#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO

#define SEND_INTERVAL		  (10 * CLOCK_SECOND)

static struct simple_udp_connection udp_conn;
#define UDP_CLIENT_PORT	8765
#define UDP_SERVER_PORT	5678

PROCESS(root_node_process, "Root Node Process");
AUTOSTART_PROCESSES(&root_node_process);

static void udp_rx_callback(struct simple_udp_connection *c,
                            const uip_ipaddr_t *sender_addr,
                            uint16_t sender_port,
                            const uip_ipaddr_t *receiver_addr,
                            uint16_t receiver_port,
                            const uint8_t *data,
                            uint16_t datalen)
{
    LOG_INFO("Received data from ");
    LOG_INFO_6ADDR(sender_addr);
    LOG_INFO(" on port %d: ", sender_port);
    LOG_INFO("%.*s\n", datalen, (char *)data);
}

PROCESS_THREAD(root_node_process, ev, data)
{
    // static struct etimer periodic_timer;
    // static char str[32];
    // uip_ipaddr_t dest_ipaddr;
    // static uint32_t tx_count;
    // static uint32_t missed_tx_count;
    
    PROCESS_BEGIN();

    /* Initialize UDP Connection */
    simple_udp_register(&udp_conn, UDP_CLIENT_PORT, NULL,
                        UDP_SERVER_PORT, udp_rx_callback);

    // etimer_set(&periodic_timer, random_rand() % SEND_INTERVAL);

    // initialize the RPL routing and set the root node to coordinator
    NETSTACK_ROUTING.root_start();
    NETSTACK_MAC.on();
    
// #if WITH_PERIODIC_ROUTES_PRINT
//   static struct etimer et;
//   /* Print out routing tables every minute */
//   etimer_set(&et, CLOCK_SECOND * 60);
//   while(1) {
//     /* Used for non-regression testing */
//     #if (UIP_MAX_ROUTES != 0)
//       PRINTF("Routing entries: %u\n", uip_ds6_route_num_routes());
//     #endif
//     #if (UIP_SR_LINK_NUM != 0)
//       PRINTF("Routing links: %u\n", uip_sr_num_nodes());
//     #endif
//     PROCESS_YIELD_UNTIL(etimer_expired(&et));
//     etimer_reset(&et);
//   }
// #endif /* WITH_PERIODIC_ROUTES_PRINT */
    while(1) {
        PROCESS_WAIT_EVENT();
    }

    PROCESS_END();
}
