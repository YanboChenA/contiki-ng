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

#define DATA_SIZE 100 // Default data size
#define SEND_INTERVAL 1 // Default send interval

#include "config.h" 

// from the struct sensor_config_t in the config.h file, 
// create a structure that contain the routine, like variation, offline, etc.
// The structure include the time and the behavior of the node in that time.
typedef enum {
    EVENT_SEND_DATA, // Send data event
    EVENT_NODE_OFFLINE, // Node offline event
    EVENT_NODE_ONLINE, //  
    EVENT_LOAD_VARIATION
} event_type_t;

typedef struct {
    clock_time_t time;
    event_type_t event_type;
} time_event_t;

PROCESS(sensor_node_process, "Sensor Node Process");
AUTOSTART_PROCESSES(&sensor_node_process);

// 模拟的发送数据函数
void send_data(void) {
    uint8_t payload[DATA_SIZE] = {0}; // 示例负载数据
    NETSTACK_NETWORK.output(NULL); // 实际发送数据
}

// 检查当前时间是否在任何失败时间段内
int check_failure_status(void) {
    // 获取当前时间（以秒为单位）
    clock_time_t current_time = clock_seconds();
    
    for (int i = 0; i < MAX_NODE_FAILURES; i++) {
        node_failure_t failure = sensor_config.node_specific[0].failures[i]; // 假设当前节点ID为0
        if (current_time >= failure.failure_time && current_time <= failure.recovery_time) {
            return 1; // 节点应该下线
        }
    }
    return 0; // 节点应该在线
}

// 根据当前时间调整发送间隔
clock_time_t adjust_send_interval(void) {
    clock_time_t interval = CLOCK_SECOND * sensor_config.send_interval; // 默认间隔
    
    // 获取当前时间（以秒为单位）
    clock_time_t current_time = clock_seconds();
    
    // 检查全局负载变化
    for (int i = 0; i < MAX_LOAD_VARIATIONS; i++) {
        load_variation_t variation = sensor_config.load_variation_global[i];
        if (current_time >= variation.start_time && current_time <= variation.end_time) {
            interval = CLOCK_SECOND / variation.interval; // 调整间隔
            break;
        }
    }
    
    return interval;
}

PROCESS_THREAD(sensor_node_process, ev, data) {
    static struct etimer send_timer;
    static clock_time_t send_interval;
    
    PROCESS_BEGIN();
    
    // 初始化发送间隔
    send_interval = adjust_send_interval();
    etimer_set(&send_timer, send_interval);

    while(1) {
        PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&send_timer));

        // 检查节点是否应该下线
        if (check_failure_status()) {
            NETSTACK_MAC.off(0); // 关闭MAC层，模拟节点下线
        } else {
            NETSTACK_MAC.on(); // 确保MAC层开启
            send_data(); // 发送数据
        }

        // 根据负载动态调整发送间隔
        send_interval = adjust_send_interval();
        etimer_set(&send_timer, send_interval);
    }

    PROCESS_END();
}