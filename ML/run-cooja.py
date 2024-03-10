import sys
import os
import shutil
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
import datetime
from generate_csc import CSC_generator
from generate_event import * 
import random
import json

# get the path of this example
SELF_PATH = os.path.dirname(os.path.abspath(__file__))
# print("Self path:", SELF_PATH)

# move two levels up
CONTIKI_PATH = os.path.dirname(SELF_PATH)
# print("CONTIKI_PATH:", CONTIKI_PATH)

# Contiki-ng/IRP/Node_with_config
CSC_PATH = os.path.normpath(os.path.join(CONTIKI_PATH, "IRP", "Node_with_config"))
# print("CSC_PATH:", CSC_PATH)

COOJA_PATH = os.path.normpath(os.path.join(CONTIKI_PATH, "tools", "cooja"))
# print("COOJA_PATH:", COOJA_PATH)

# contiki-ng/data/raw as the log save path
RAW_PATH = os.path.join(CONTIKI_PATH, "data", "raw")
# print("RAW_PATH:", RAW_PATH)

# contiki-ng/data/label as the json config path
LABEL_PATH = os.path.join(CONTIKI_PATH, "data", "label")

# cooja_input = 'cooja.csc'
cooja_input = os.path.join(CSC_PATH, 'cooja.csc')
# print("cooja_input:", cooja_input)
# cooja_output = 'COOJA.testlog'
cooja_output = os.path.join(CSC_PATH, 'COOJA.testlog')

#######################################################
# Run a child process and get its output

def run_subprocess(args, input_string):
    retcode = -1
    stdoutdata = ''
    try:
        proc = Popen(args, stdout=PIPE, stderr=STDOUT, stdin=PIPE, shell=True, universal_newlines=True)
        (stdoutdata, stderrdata) = proc.communicate(input_string)
        if not stdoutdata:
            stdoutdata = '\n'
        if stderrdata:
            stdoutdata += stderrdata + '\n'
        retcode = proc.returncode
    except OSError as e:
        sys.stderr.write("run_subprocess OSError:" + str(e))
    except CalledProcessError as e:
        sys.stderr.write("run_subprocess CalledProcessError:" + str(e))
        retcode = e.returncode
    except Exception as e:
        sys.stderr.write("run_subprocess exception:" + str(e))
    finally:
        return (retcode, stdoutdata)

#############################################################
# Run a single instance of Cooja on a given simulation script

def execute_test(cooja_file, save_time = None):
    # cleanup
    try:
        os.remove(cooja_output)
    except FileNotFoundError as ex:
        pass
    except PermissionError as ex:
        print("Cannot remove previous Cooja output:", ex)
        return False
    if save_time is None:
        save_file = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".testlog"
    else:
        save_file = save_time + ".testlog"
    
    filename = os.path.join(CSC_PATH, cooja_file)
    # print(filename)
    args = " ".join([COOJA_PATH + "/gradlew --no-watch-fs --parallel --build-cache -p", COOJA_PATH, "run --args='--contiki=" + CONTIKI_PATH, "--no-gui", "--logdir=" + CSC_PATH, filename + "'"])
    sys.stdout.write("  Running Cooja, args={}\n".format(args))

    (retcode, output) = run_subprocess(args, '')
    if retcode != 0:
        sys.stderr.write("Failed, retcode=" + str(retcode) + ", output:")
        sys.stderr.write(output)
        return False

    sys.stdout.write("  Checking for output...")

    is_done = False
    with open(cooja_output, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line == "TEST OK":
                sys.stdout.write(" done.\n")
                is_done = True
                continue

    if not is_done:
        sys.stdout.write("  test failed.\n")
        return False
    
    save_logfile(save_file)

    sys.stdout.write(" test done\n")
    return True

#######################################################
# Move the logfile to the save path and rename it
# Rename format should be current date and time
def save_logfile(file_name=None):
    if file_name is None:
        file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".testlog"
    
    file_name = os.path.join(RAW_PATH, file_name)
    # move cooja_output to save path
    try:
        shutil.move(cooja_output, file_name)
    except:
        # sys.stdout.write("Cannot move Cooja output to save path.")
        print("Cananot move Cooja output to save path.")
        return False
    # sys.stdout.write("Cooja output saved as:", file_name)
    print("Cooja output saved as:", file_name)
    return True
    
def generate_csc_file(node_num = 8, env_label = 0):
    """
    
    Args:
        node_num (int): the number of nodes in the simulation
        env_label (int): the label of the environment 
                        0 : For normal backgtound noise, default -85
                        1 : For medium background noise, -80 
                        2 : For High background noise, -75
    """
    csv_generator = CSC_generator()
    csv_generator.reset()
    csv_generator.set_bg_noise_mean(-85 + env_label * 5)
    node_map = generate_node_map(node_num)
    for i,(x,y) in node_map.items():
        if i == 1:
            pass
        else:
            csv_generator.add_mote(i, x, y)
    csv_generator.save(cooja_input)
    return node_map
            
def generate_node_map(num):
    """Generate a map of nodes with random x and y coordinates, and the node should not far away the neighbor more than 20.

    Args:
        num (int): number of nodes

    Returns:
        dict: node_map: {node_id: (x, y)}
    """
    # set random seed
    # random.seed(1)
    node_map = {}
    for i in range(1,num+1):
        if i == 1:
            # sink node
            node_map[i] = (0, 0)
            continue
        else:

            #  x and y coordinate: float in range (0, 100)
            x_coordinate = random.uniform(-75, 75)
            y_coordinate = random.uniform(-75, 75)

            node_map[i] = (x_coordinate, y_coordinate)
    return node_map

def save_json(node_map, label_list, env_labal, save_time):
    """Save the node map and label list to a json file

    Args:
        node_map (dict): {node_id: (x, y)}
        label_list (list): list of labels
        env_labal (int): the label of the environment
        save_time (str): the time of the simulation
    """
    json_file = os.path.join(LABEL_PATH, save_time + ".json")
    data = {
        "node_map": node_map,
        "label_list": label_list,
        "env_label": env_labal
    }
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

def run_simulation(node_num=8,env_label=0):
    """Run the simulation with the given node number and environment label

    Args:
        node_num (int, optional): Node numbers. Defaults to 8.
        env_label (int, optional): The environment label. Defaults to 0.
    """    
    
    node_map = generate_csc_file(node_num, env_label)
    
    label_list = generate_labels()
    event_list = generate_events(label_list)
    generate_events_h(event_list, os.path.join(CSC_PATH, "events.h"))
    
    save_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    save_json(node_map, label_list, env_label, save_time)
    execute_test(cooja_input,save_time)
    
def generate_random_node_num_and_env_label():
    node_num = random.randint(8,16)
    env_label = random.randint(0,2)
    return node_num, env_label
    
#######################################################
# Run the application

def main():
    input_file = cooja_input
    if len(sys.argv) > 1:
        # change from the default
        input_file = sys.argv[1]

    # print(os.R_OK)

    if not os.access(input_file, os.R_OK):
        print('Simulation script "{}" does not exist'.format(input_file))
        exit(-1)

    print('Using simulation script "{}"'.format(input_file))
    if not execute_test(input_file):
        exit(-1)

#######################################################

if __name__ == '__main__':
    # main()
    for i in range(1):
        print("Current runtimes:", i)
        node_num,env_label = generate_random_node_num_and_env_label()
        run_simulation(8, env_label)
