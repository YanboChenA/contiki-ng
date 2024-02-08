#ifndef SENSOR_STRUCT_H
#define SENSOR_STRUCT_H

typedef struct {
    unsigned long timestamp;  // 
    char sensor_id;           // 
    float temperature;        // 
    float humidity;           // 
    float pressure;           // 
    float gas;                // 
    float accelerometer;      // 
    float light;              // 
    float mic;                // 
    float rssi;               
} SensorData;

#endif // SENSOR_STRUCT_H
