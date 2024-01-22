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
#include "net/routing/rpl-classic/rpl.h"

#define DEBUG DEBUG_PRINT
#include "net/ipv6/uip-debug.h"

#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO
#define UDP_CLIENT_PORT 8765
#define UDP_SERVER_PORT 5678
#define SEND_INTERVAL (60 * CLOCK_SECOND)

PROCESS(sub_node_process, "Sub Node Process");
AUTOSTART_PROCESSES(&sub_node_process);

static struct simple_udp_connection udp_conn;

PROCESS_THREAD(sub_node_process, ev, data)
{
    static struct etimer periodic_timer;
    uip_ipaddr_t dest_ipaddr;
    PROCESS_BEGIN();

    /* Initialize UDP Connection */
    simple_udp_register(&udp_conn, UDP_CLIENT_PORT, NULL,
                        UDP_SERVER_PORT, NULL);

    etimer_set(&periodic_timer, SEND_INTERVAL);

    while(1) {
        PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&periodic_timer));

        if(!tsch_is_associated) {
            printf("Not associated, drop packet\n");
        } else {
            char *msg = "Hello";
            NETSTACK_ROUTING.get_root_ipaddr(&dest_ipaddr);
            if(!uip_is_addr_unspecified(&dest_ipaddr)) {
                simple_udp_sendto(&udp_conn, msg, strlen(msg), &dest_ipaddr);
            } else {
                printf("Root address not found\n");
            }
        }

        etimer_reset(&periodic_timer);
    }

    PROCESS_END();
}