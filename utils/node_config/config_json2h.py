import os
import json


class ConfigGenerator:
    def __init__(self):
        self.config = {
            "config_limits": {
                "MAX_NODE_SPECIFIC": 5,
                "MAX_LOAD_VARIATIONS": 5,
                "MAX_NODE_FAILURES": 5
            },
            "network_config": {},
            "load_variation_global": [],
            "node_specific": []
            #TODO may be add packet size later
        }

    def load_from_json(self, filepath):
        with open(filepath, 'r') as file:
            self.config = json.load(file)
    
    def set_network_config(self, send_interval, packet_size, max_runtime):
        self.config["network_config"] = {
            "send_interval": send_interval,
            "packet_size": packet_size,
            "max_runtime": max_runtime
        }
    
    def add_global_load_variation(self, start_time, end_time, interval, packet_size):
        variation = {
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval,
            "packet_size": packet_size
        }
        self.config["load_variation_global"].append(variation)
    
    def add_node_specific_config(self, node_id, load_variations=[], failures=[]):
        node_config = {
            "node_id": node_id,
            "load_variation": load_variations,
            "failures": failures
        }
        self.config["node_specific"].append(node_config)

    def generate_config_h(self, output_file):
        with open(output_file, 'w') as file:
            file.write('#ifndef CONFIG_H_\n')
            file.write('#define CONFIG_H_\n\n')
            file.write('#include "config_config.h"\n\n')
            
            # Config limits definitions
            config_limits = self.config['config_limits']
            for key, value in config_limits.items():
                file.write(f'#define {key} {value}\n')
            file.write('\n')
            
            # Network Config
            net_config = self.config['network_config']

            # Send Interval, Packet Size, Max Runtime
            file.write(f'#define SEND_INTERVAL          ({net_config.get("send_interval", 0)} * CLOCK_SECOND)\n')
            file.write(f'#define PACKET_SIZE {net_config.get("packet_size", 0)}\n')
            file.write(f'#define MAX_RUNTIME            ({net_config.get("max_runtime", 0)} * CLOCK_SECOND)\n\n')

            file.write('const sensor_config_t sensor_config = {\n')
            # file.write(f'  send_interval = {net_config.get("send_interval", 0)},\n')
            # file.write(f'  packet_size = {net_config.get("packet_size", 0)},\n')
            # file.write(f'  max_runtime = {net_config.get("max_runtime", 0)},\n')
            
            # Global Load Variation
            file.write('  load_variation_global = {\n')
            for variation in self.config.get('load_variation_global', []):
                file.write('    {')
                file.write(f'start_time = {variation["start_time"]}, ')
                file.write(f'end_time = {variation["end_time"]}, ')
                file.write(f'interval = {variation["interval"]}, ')
                file.write(f'packet_size = {variation["packet_size"]}')
                file.write('},\n')
            file.write('  },\n')
            
            # Node Specific Config
            file.write('  node_specific = {\n')
            for node in self.config.get('node_specific', []):
                file.write('    {\n')
                file.write(f'      node_id = {node["node_id"]},\n')
                
                # Load Variations
                file.write('      load_variations = {\n')
                for lv in node.get('load_variation', []):
                    file.write('        {')
                    file.write(f'start_time = {lv["start_time"]}, ')
                    file.write(f'end_time = {lv["end_time"]}, ')
                    file.write(f'interval = {lv["interval"]}, ')
                    file.write(f'packet_size = {lv["packet_size"]}')
                    file.write('},\n')
                file.write('      },\n')
                
                # Failures
                file.write('      failures = {\n')
                for failure in node.get('failures', []):
                    file.write('        {')
                    file.write(f'failure_time = {failure["failure_time"]}, ')
                    file.write(f'recovery_time = {failure.get("recovery_time", 0)}')
                    file.write('},\n')
                file.write('      },\n')
                file.write('    },\n')
            file.write('  }\n')
            file.write('};\n\n')
            
            file.write('#endif /* CONFIG_H_ */\n')


if __name__ == "__main__":
    # # get current work directory
    # cwd = os.getcwd()
    folder = "/home/yanbo/contiki-ng/IRP/Node_with_config/configs"
    config_file = os.path.join(folder, "config.json")
    output_file = os.path.join(folder, "config.h")
    # generate_config_h(config_file, output_file)
    cg = ConfigGenerator()
    cg.load_from_json(config_file)
    cg.generate_config_h(output_file)