from utils.common_functions import check_os
from questionnaire.trout import trgout
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


def send_trigger(p, code, numlns=8):
    """
        Invia un codice di trigger e lo converte in binario tramite porta parallela.

        Args:
            p : porta parallela
            code (int): Il codice numerico da inviare.
            numlns (int, opzionale): Il numero di linee (o pin) da utilizzare
            per la rappresentazione binaria del codice. Default è 8.

        Returns:
            None
    """
    
    # Invia il valore alla porta parallela, attende 10ms e poi resetta la porta
    p.setData(code)
    time.sleep(0.01)
    p.setData(0)    

# Definizione dei codici trigger
RC_TRIG = 10  # Start Recording
BG_TRIG = 20 # Start Experiment
A_TRIG = 22 # Acoustic stimula
S_TRIG = 28  # Sham Stimulation
AS_TRIG = 30  # Alarm Sound
I_TRIG = 26 # Interruption
ED_TRIG = 40  # Stop Experiment

def start_eeg_recording(p):
    print("Avvio registrazione EEG")
    send_trigger(RC_TRIG)

def stop_eeg_recording(p):
    print("Arresto registrazione EEG")
    send_trigger(ED_TRIG)

if __name__ == "__main__":
    # Inizializzazione della porta parallela
    address = 0x378
    p = parallel.Parallel()
     
    start_eeg_recording(p)
    time.sleep(5)  
    stop_eeg_recording(p)
    time.sleep(5)
    send_trigger(p, BG_TRIG)
    time.sleep(5)
    send_trigger(p, A_TRIG)
    time.sleep(5)
    send_trigger(p, S_TRIG)
    time.sleep(5)
    send_trigger(p, I_TRIG)
    time.sleep(5)
    send_trigger(p, ED_TRIG)
