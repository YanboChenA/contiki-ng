#ifndef CONFIG_H_
#define CONFIG_H_

#include "config_config.h"

#define MAX_NODE_SPECIFIC 5
#define MAX_LOAD_VARIATIONS 5
#define MAX_NODE_FAILURES 5

const sensor_config_t sensor_config = {
  .send_interval = 10,
  .packet_size = 120,
  .max_runtime = 3600,
  .load_variation_global = {
    {.start_time = 100, .end_time = 200, .interval = 15, .packet_size = 150},
  },
  .node_specific = {
    {
      .node_id = 1,
      .load_variations = {
        {.start_time = 300, .end_time = 400, .interval = 20, .packet_size = 180},
      },
      .failures = {
        {.failure_time = 1500, .recovery_time = 1600},
      },
    },
    {
      .node_id = 2,
      .load_variations = {
        {.start_time = 500, .end_time = 600, .interval = 25, .packet_size = 200},
      },
      .failures = {
        {.failure_time = 2000, .recovery_time = 2100},
      },
    },
  }
};

#endif /* CONFIG_H_ */
