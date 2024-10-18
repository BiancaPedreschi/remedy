from utils.common_functions import check_os
import numpy as np
import csv
import os
import pandas as pd
import random
from psychopy import visual, core, sound, event, monitors
from psychopy.hardware import keyboard
from psychopy import prefs
import parallel
import time
# from psychtoolbox import audio, GetSecs
import sounddevice as sd
import scipy.io.wavfile as sw
from questionnaire.trout import trgout
import threading

# prefs.hardware['audioLib'] = ['ptb', 'pyo', 'pygame']
prefs.hardware['audioLib'] = ['sounddevice', 'pyo', 'pygame', 'PTB']
prefs.hardware['audioDevice'] = 'sysdefault'
prefs.hardware['audioLatencyMode'] = 3

if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
    
if check_os() in ['Linux']:
    kb = keyboard.Keyboard(device=-1)
elif check_os() in ['Windows', 'macOS']:
    kb = None

# Inizializzazione della porta parallela LPT1
address = 0x378
try:
    p = parallel.Parallel()
    print("Parallel port opened")
except Exception as e:
    p = None
    print("Error in parallel port configuration")

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
        #trigger_bin = trgout(code, numlns)
        print(f"Trigger inviato: {code}, binario: {code}")
        p.setData(code)
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

# RC_TRIG = 32  # Start Recording
# BG_TRIG = 80 # Start Experiment
# A_TRIG = 96 # Acoustic stimula
# S_TRIG = 48  # Sham Stimulation
# AS_TRIG = 64  # Alarm Sound
# I_TRIG = 112 # Interruption
# ED_TRIG = 128  # Stop Experiment

def start_eeg_recording(p):
    print("Avvio registrazione EEG")
    send_trigger_thread(p=p, code=RC_TRIG)

def stop_eeg_recording(p):
    print("Arresto registrazione EEG")
    send_trigger_thread(p=p, code=ED_TRIG)

# Esempio di utilizzo
if __name__ == "__main__":
    # start_eeg_recording(p)
    # time.sleep(60)  
    send_trigger_thread(p, BG_TRIG)
    time.sleep(2)
    send_trigger_thread(p, N2_TRIG)
    time.sleep(2)
    send_trigger_thread(p, REM_TRIG)
    time.sleep(2)
    send_trigger_thread(p, AS_TRIG)
    time.sleep(2)
    send_trigger_thread(p, S_TRIG)
    time.sleep(2)
    send_trigger_thread(p, I_TRIG)
    # stop_eeg_recording(p)
    # time.sleep(5)