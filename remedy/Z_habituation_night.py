from remedy.utils.common_functions import check_os
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
    
from psychopy.hardware import keyboard
from psychopy import visual, core
import sounddevice as sd
import soundfile as sf
import parallel
import os.path as op

from remedy.config.config import read_config
from remedy.utils.find_devices import find_device
from remedy.utils.common_functions import (send_trigger_thread, wait_kbd_emo, 
                                           get_meta, show)


def play_pink_noise(pink_noise):
    sd.play(pink_noise, loop=True)
    return pink_noise


def stop_pink_noise():
    sd.stop()
    return 


def task_Z():
    
    config = read_config()
    data_dir = config['paths']['data']

    # Set sounds
    pink_noise_file = op.join(data_dir, 'pwd', 'night_stim', 'PN.wav')
    alarm_path = op.join(data_dir, 'alarm_beep.wav')
    
    # Inizializzazione della porta parallela LPT1
    try:
        p = parallel.Parallel()
        print("Porta parallela aperta")
    except Exception as e:
        p = None
        print("Errore apertura porta parallela")
    
    # Set triggers code
    ST_TRIG = 20 # Start pink noise
    AL_TRIG = 28 # Start alarm
    NA_TRIG = 30 # Natural awakening
    
    win = visual.Window(fullscr=False, color="black", units="norm")
    instruction_text = visual.TextStim(win, text='', pos=(0, 0), height=0.05)
    
    if check_os() in ['Linux']:
        kb = keyboard.Keyboard(device=-1)
    elif check_os() in ['Windows', 'macOS']:
        kb = None
    
    dev_hp, dev_sp = find_device()
    sd.default.device = dev_hp
    
    instruction_text.text = "Press 'P' to start pink noise"
    instruction_text.draw()
    win.flip()
    
    k = None
    while k != 'p':
        keys = kb.waitKeys(keyList=['p'])
        k = keys[0].name

    
    send_trigger_thread(p, ST_TRIG)
    play_pink_noise(sf.read(pink_noise_file)[0])
    
    instruction_text.text = "Press 'A' to start alarm, or 'esc' to quit pink noise"
    instruction_text.draw()
    win.flip()
    
    k = None
    while k != 'a' and k != 'escape':
        keys = kb.waitKeys(keyList=['a', 'escape'])
        k = keys[0].name
        
    if k == 'a':
        send_trigger_thread(p, AL_TRIG)
        stop_pink_noise()
        sd.default.device = dev_sp
        sd.play(sf.read(alarm_path)[0])
        sd.wait()
    elif k == 'escape':
        send_trigger_thread(p, NA_TRIG)
        stop_pink_noise()
        
    return


if __name__ == '__main__':
    task_Z()
    