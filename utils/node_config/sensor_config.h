#ifndef CONFIG_CONFIG_H_
#define CONFIG_CONFIG_H_

#include <stdint.h> // For using standard integer types

// #define MAX_LOAD_VARIATIONS 5
// #define MAX_NODE_SPECIFIC 5
// #define MAX_NODE_FAILURES 5

typedef struct {
    uint32_t start_time;
    uint32_t end_time;
    int interval;
    int packet_size;
} load_variation_t;

typedef struct {
    uint32_t failure_time;
    uint32_t recovery_time;
} node_failure_t;

typedef struct {
    uint8_t node_id;
    load_variation_t load_variations[];
    node_failure_t failures[];
} node_specific_t;

typedef struct {
    int send_interval;
    int packet_size;
    int max_runtime;
    load_variation_t load_variation_global[];
    node_specific_t node_specific[];
} sensor_config_t;

// void config_load(const char *json_data, sensor_config_t *config);

#endif /* CONFIG_CONFIG_H_ */
