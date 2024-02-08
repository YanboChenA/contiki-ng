#include "contiki.h"
#include "net/ipv6/simple-udp.h"
#include "net/mac/tsch/tsch.h"
#include "net/mac/tsch/tsch-schedule.h"
#include "lib/random.h"
#include "sys/node-id.h"
#include <string.h>
#include "net/packetbuf.h"

#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO

#define UDP_PORT 8765

static struct simple_udp_connection udp_conn;

PROCESS(root_node_process, "Root Node Process");
AUTOSTART_PROCESSES(&root_node_process);

static void udp_rx_callback(struct simple_udp_connection *c,
                            const uip_ipaddr_t *sender_addr,
                            uint16_t sender_port,
                            const uip_ipaddr_t *receiver_addr,
                            uint16_t receiver_port,
                            const uint8_t *data,
                            uint16_t datalen) {
    int16_t rssi = packetbuf_attr(PACKETBUF_ATTR_RSSI);
    uint8_t lqi = packetbuf_attr(PACKETBUF_ATTR_LINK_QUALITY);

    LOG_INFO("Received data from ");
    LOG_INFO_6ADDR(sender_addr);
    LOG_INFO_(", RSSI %d, LQI %u\n", rssi, lqi);
    // 在这里你可以进一步处理接收到的数据
}

PROCESS_THREAD(root_node_process, ev, data) {
    PROCESS_BEGIN();

    // 设置该节点为网络的根节点
    if (node_id == 1) { 
        NETSTACK_ROUTING.root_start();
    }
    NETSTACK_MAC.on();

    // 初始化UDP连接，用于接收数据
    simple_udp_register(&udp_conn, UDP_PORT, NULL, UDP_PORT, udp_rx_callback);

    while(1) {
        PROCESS_WAIT_EVENT();
        // 在这里，你可以添加更多的代码来处理其他事件
    }

    PROCESS_END();
}