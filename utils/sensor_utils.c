#include "sensor_utils.h"


extern SensorData sensor_data[];

SensorData get_sensor_data(char sensor_id, int index) {
    int count = 0;
    for (int i = 0; i < sensor_data_length; i++) {
        if (sensor_data[i].sensor_id == sensor_id) {
            if (count == index) {
                return sensor_data[i];
            }
            count++;
        }
    }

    // Return an empty SensorData struct if not found
    SensorData empty;
    memset(&empty, 0, sizeof(empty));
    return empty;
}