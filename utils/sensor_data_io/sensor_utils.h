#ifndef SENSOR_UTILS_H
#define SENSOR_UTILS_H

#include "sensor_struct.h"
#include <string.h>
#include "sensor_data.h"

// Function to get the data for a given sensor ID and its occurrence index
SensorData get_sensor_data(char sensor_id, int index);


#endif // SENSOR_UTILS_H
