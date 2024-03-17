'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-10 18:49:06
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-17 15:44:34
FilePath: /contiki-ng/ML/generate_event.py
Description: 
'''
import os
import random

def generate_labels(interval = 30, total_run_time = 3600):
    labels_num = total_run_time // interval
    labels = [random.randint(0, 2) for i in range(labels_num)]
    return labels

def generate_events(labels):
    event_list = []
    current_time = 0  # Start time for the first label event
    label_interbal = 30  # Seconds
    
    default_interval = (15,18)
    default_packet_size = (50,60)
    
    medium_interval = (8,12)
    medium_packet_size = (60,70)
    
    high_interval = (2,5)
    high_packet_size = (70,80)
    
    
    # default_interval = random.randint(10, 15)  # Normal load sending interval in seconds, randomly between 10 to 15
    # default_packet_size = random.randint(50, 60)  # Normal load packet size, randomly between 50 to 60

    for label in labels:
        if label == 0:  # Normal load
            event_list.append({
                "time": current_time,
                "event_type": "EVENT_LOAD_VARIATION",
                "target_send_interval": random.randint(*default_interval),
                "target_packet_size": random.randint(*default_packet_size),
                "node_id": -1  # Global event
            })
        elif label == 1:  # Medium load, randomly select a time within 10 to 20 seconds
            event_list.append({
                "time": current_time,  
                "event_type": "EVENT_LOAD_VARIATION",
                "target_send_interval": random.randint(*medium_interval),  # Randomly between 10 to 20 seconds
                "target_packet_size": random.randint(*medium_packet_size),  # Randomly increase packet size
                "node_id": -1
            })
        elif label == 2:  # High load
            event_list.append({
                "time": current_time,
                "event_type": "EVENT_LOAD_VARIATION",
                "target_send_interval": random.randint(*high_interval),
                "target_packet_size": random.randint(*high_packet_size),
                "node_id": -1
            })

        current_time += label_interbal  # Move to the next event time, ensuring a 30s interval between labels

    # Sort the event list by time, though it should already be in order
    event_list.sort(key=lambda event: event["time"])

    return event_list


def generate_events_h(event_list, output_file):
    with open(output_file, 'w') as file:
        file.write('#ifndef EVENTS_H_\n')
        file.write('#define EVENTS_H_\n\n')
        file.write('#include "contiki.h"\n\n')

        # Event type enum
        file.write('typedef enum {\n')
        file.write('    EVENT_FAILURE,\n')
        file.write('    EVENT_RECOVERY,\n')
        file.write('    EVENT_LOAD_VARIATION\n')
        file.write('} event_type_t;\n\n')

        # Event struct
        file.write('typedef struct {\n')
        file.write('    clock_time_t time;\n')
        file.write('    event_type_t event_type;\n')
        file.write('    int target_send_interval;\n')
        file.write('    int target_packet_size;\n')
        file.write('    int node_id;\n')  # Added node_id
        file.write('} node_event_t;\n\n')

        event_list_size = len(event_list)
        file.write('int event_list_size = {};\n\n'.format(event_list_size))

        # Events array
        file.write('node_event_t event_list[] = {\n')
        for event in event_list:
            file.write('    {{.time = {}, .event_type = {}, .target_send_interval = {}, .target_packet_size = {}, .node_id = {}}},\n'.format(
                event["time"], event["event_type"], event["target_send_interval"], event["target_packet_size"], event["node_id"]))
        file.write('};\n\n')

        file.write('#endif /* EVENTS_H_ */\n')
  

if __name__ == "__main__":
    save_folder = f"/home/yanbo/contiki-ng/IRP/event_files"
    import os

    labels = [2 for _ in range(120)]
    event_list = generate_events(labels)
    output_file = os.path.join(save_folder, "event_HL.h")
    generate_events_h(event_list, output_file)


