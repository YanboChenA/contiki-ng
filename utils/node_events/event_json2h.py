import os
import json

class EventGenerator:
    def __init__(self):
        self.config = {}
        self.event_list = []

    def load_from_json(self, filepath):
        with open(filepath, 'r') as file:
            self.config = json.load(file)

    def convert_to_event_list(self):
        # Global load variations
        for variation in self.config.get('load_variation_global', []):
            # Start event
            self.event_list.append({
                "time": variation["start_time"],
                "event_type": "EVENT_LOAD_VARIATION",
                "target_send_interval": variation["interval"],
                "target_packet_size": variation["packet_size"],
                "node_id": -1  # Global event, no specific node ID
            })
            # End event
            self.event_list.append({
                "time": variation["end_time"],
                "event_type": "EVENT_LOAD_VARIATION",
                "target_send_interval": 0,  # Assuming no change at end
                "target_packet_size": 0,    # Assuming no change at end
                "node_id": -1
            })

        # Node specific configurations
        for node in self.config.get('node_specific', []):
            node_id = node["node_id"]
            for lv in node.get('load_variation', []):
                # Start event
                self.event_list.append({
                    "time": lv["start_time"],
                    "event_type": "EVENT_LOAD_VARIATION",
                    "target_send_interval": lv["interval"],
                    "target_packet_size": lv["packet_size"],
                    "node_id": node_id
                })
                # End event
                self.event_list.append({
                    "time": lv["end_time"],
                    "event_type": "EVENT_LOAD_VARIATION",
                    "target_send_interval": 0,  # Assuming no change at end
                    "target_packet_size": 0,    # Assuming no change at end
                    "node_id": node_id
                })
            for failure in node.get('failures', []):
                # Failure event
                self.event_list.append({
                    "time": failure["failure_time"],
                    "event_type": "EVENT_FAILURE",
                    "target_send_interval": 0,  # No change for failure events
                    "target_packet_size": 0,    # No change for failure events
                    "node_id": node_id
                })
                # Recovery event, if exists
                if "recovery_time" in failure:
                    self.event_list.append({
                        "time": failure["recovery_time"],
                        "event_type": "EVENT_RECOVERY",
                        "target_send_interval": 0,  # No change for recovery events
                        "target_packet_size": 0,    # No change for recovery events
                        "node_id": node_id
                    })

        # Sort the event list by time
        self.event_list.sort(key=lambda event: event["time"])

    def generate_events_h(self, output_file):
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
            
            event_list_size = len(self.event_list)
            # file.write('int event_list_size = '+event_list_size+"\n")
            file.write('int event_list_size = {};\n\n'.format(event_list_size))
                       
            # Events array
            file.write('node_event_t event_list[] = {\n')
            for event in self.event_list:
                file.write('    {{.time = {}, .event_type = {}, .target_send_interval = {}, .target_packet_size = {}, .node_id = {}}},\n'.format(
                    event["time"], event["event_type"], event["target_send_interval"], event["target_packet_size"], event["node_id"]))
            file.write('};\n\n')

            file.write('#endif /* EVENTS_H_ */\n')


if __name__ == "__main__":
    folder = "/home/yanbo/contiki-ng/IRP/Node_with_config/configs"
    json_file = os.path.join(folder, "config.json")
    output_file = os.path.join(folder, "events.h")
    eg = EventGenerator()
    eg.load_from_json(json_file)
    eg.convert_to_event_list()
    eg.generate_events_h(output_file)
