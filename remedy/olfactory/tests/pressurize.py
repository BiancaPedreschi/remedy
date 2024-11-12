import os
import sys
sys.path.insert(0, os.getcwd())
from remedy.olfactometer_controller import olfactometer
import time

port = "/dev/cu.usbmodem20220051"
#port = "/dev/ttyACM0"
baudrate = 9600


output_directory = '/Users/foscagiannotti/Desktop/project_remedy/output_olfactometer'
output_filename = 'prova.txt'
output_file_path = os.path.join(output_directory, output_filename)

monitor = olfactometer(output_file_path)
monitor.set_serial(port, baudrate=9600)
monitor.open(timeout=None)

monitor.run()
monitor.write('C M;;;;;;;')
time.sleep(.5)
monitor.write('E 1')
time.sleep(.5)
monitor.write('S 0')
time.sleep(10)

##
#monitor.write('S 1')
#time.sleep(600)
monitor.write('S 0')
time.sleep(120)
# monitor.write('S 2')
# time.sleep(120)
# monitor.write('S 0')
# time.sleep(60)
# monitor.write('S 0')
# time.sleep(30)
# monitor.write('S 2')
# time.sleep(10)
# monitor.write('S 4')
# time.sleep(10)
# monitor.write('S 0')
# time.sleep(10)

monitor.write('E 0')
time.sleep(0.5)
monitor.stop()
time.sleep(0.5)
monitor.close()