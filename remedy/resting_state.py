from utils.common_functions import check_os, get_meta_night
from config.config import read_config
from questionnaire.trout import trgout
from psychopy import visual, core, sound, event, monitors
from psychopy.hardware import keyboard
from psychopy import prefs
import parallel
import time
import scipy.io.wavfile as sw
from scipy.signal import lfilter
import threading


if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
    
if check_os() in ['Linux']:
    kb = keyboard.Keyboard(device=-1)
elif check_os() in ['Windows', 'macOS']:
    kb = keyboard.Keyboard()  

# # Inizializzazione della porta parallela
address = 0x3EFC
p = parallel.Parallel()

def send_trigger_thread(p, code, numlns=8):
    """
    Sends a trigger code converted to binary via serial port in a separate thread.

    Args:
        p : porta parallela
        code (int): The numeric code to send.
        numlns (int, optional): The number of lines (or pins) to use for the binary representation of the code. Default is 8.

    Returns:
        None
    """
    def trigger():
        trigger_bin = trgout(code, numlns)
        print(f"Trigger inviato: {code}, binario: {trigger_bin}")
        trigger_value = int(''.join(map(str, trigger_bin)), 2)
        p.setData(trigger_value)
        time.sleep(0.01)
        p.setData(0)
    
    threading.Thread(target=trigger).start()

# Definizione dei codici trigger
RC_TRIG = 10  # Start Recording
BG_TRIG = 20 # Start Experiment
REM_TRIG = 22 # REM Stimulation
N2_TRIG = 24 # N2 
S_TRIG = 28  # Sham Stimulation
AS_TRIG = 30  # Alarm Sound
I_TRIG = 26 # Interruption
ED_TRIG = 40  # Stop Experiment

def start_eeg_recording(p):
    print("Avvio registrazione EEG")
    # send_trigger_thread(p, RC_TRIG)

def stop_eeg_recording(p):
    print("Arresto registrazione EEG")
    # send_trigger_thread(p, ED_TRIG)
def main():

    win = visual.Window(fullscr=False, color="black", units="norm")
    instruction_text = visual.TextStim(win, text='', pos=(0, 0), height=0.05)
   
    # Ottieni le informazioni una sola volta all'inizio
    outputname = get_meta_night()
    participant_id = outputname[0]
    session = int(outputname[1])
    sex = outputname[2]
 
    config = read_config()
    parent_dir = config['paths']['parent']
    
    for i in range(3):
        start_eeg_recording(p)
        time.sleep(120)
        stop_eeg_recording(p)
        time.sleep(30)
    

if __name__ == "__main__":
    main()