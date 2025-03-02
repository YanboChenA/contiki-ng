'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-14 16:23:46
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-14 17:02:02
FilePath: /contiki-ng/IRP/Node_with_config_optimization/run-cooja.py
Description: 
'''
#!/usr/bin/env python3

import sys
import os
import shutil
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
import datetime

# get the path of this example
SELF_PATH = os.path.dirname(os.path.abspath(__file__))
# print("Self path:", SELF_PATH)

# move two levels up
CONTIKI_PATH = os.path.dirname(os.path.dirname(SELF_PATH))
# print("CONTIKI_PATH:", CONTIKI_PATH)

COOJA_PATH = os.path.normpath(os.path.join(CONTIKI_PATH, "tools", "cooja"))
# print("COOJA_PATH:", COOJA_PATH)

# contiki-ng/data/raw as the save path
SAVE_PATH = os.path.join(CONTIKI_PATH, "data", "raw")
print("SAVE_PATH:", SAVE_PATH)

# cooja_input = 'cooja.csc'
cooja_input = os.path.join(SELF_PATH, 'cooja.csc')
# print("cooja_input:", cooja_input)
# cooja_output = 'COOJA.testlog'
cooja_output = os.path.join(SELF_PATH, 'COOJA.testlog')





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

def execute_test(cooja_file):
    # cleanup
    try:
        os.remove(cooja_output)
    except FileNotFoundError as ex:
        pass
    except PermissionError as ex:
        print("Cannot remove previous Cooja output:", ex)
        return False

    save_file = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".testlog"

    filename = os.path.join(SELF_PATH, cooja_file)
    # print(filename)
    args = " ".join([COOJA_PATH + "/gradlew --no-watch-fs --parallel --build-cache -p", COOJA_PATH, "run --args='--contiki=" + CONTIKI_PATH, "--no-gui", "--logdir=" + SELF_PATH, filename + "'"])
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
    
    file_name = os.path.join(SAVE_PATH, file_name)
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
    main()
