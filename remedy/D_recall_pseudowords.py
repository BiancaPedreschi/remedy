from remedy.utils.common_functions import check_os
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
from psychopy import visual, core, monitors, sound
from psychopy.hardware import keyboard
import os
import os.path as op
import numpy as np
import random
import pandas as pd
import parallel
import sounddevice as sd
import soundfile as sf
from datetime import datetime

from remedy.utils.common_functions import (wait_kbd_emo, get_meta, show,
                                           send_trigger_thread)
from remedy.utils.find_devices import find_device
from remedy.utils.audio_recorder import save_recording_audio
from remedy.config.config import read_config


def task_D():
    
    devices = find_device()
    dev_sp = devices[1]
    config = read_config()
    parent_dir = config['paths']['parent']
    data_dir = config['paths']['data']
    results_dir = config['paths']['results']
    all_combinations_path =  op.join(parent_dir, 'combinations', 
                                     'all_combinations_pseudo_day.csv')
    all_combinations_df = pd.read_csv(all_combinations_path)
    
    # # Define parallel port
    try:
        p = parallel.Parallel()
        print("Porta parallela aperta")
    except Exception as e:
        p = None
        print("Errore apertura porta parallela")
    
    # Define trigger
    SN_TRIG = 26 # Trigger for sound presentation

    outputname = get_meta()
    subject_id = outputname[0]
    session = int(outputname[1])

    # Filtra il DataFrame per subject_id e session
    filtered_df = all_combinations_df[
        (all_combinations_df['Participant_ID'] == subject_id) & 
        (all_combinations_df['Session'] == session)]
    
    # Ottieni i percorsi delle pseudoparole
    audio_paths = filtered_df['Pseudo'].tolist()  # Moltiplica per 34 per includere la ripetizione
    # random.shuffle(audio_paths)
    
    output_directory = op.join(results_dir, f'RY{subject_id:03d}', 
                               f'N{session}', 'task_D')
    os.makedirs(output_directory, exist_ok=True)

    sd.default.device = dev_sp
    sounds = [sf.read(audio)[0] for audio in audio_paths]

    # Set psychopy video and keyboard settings
    widthPix = 1920  # screen width in px
    heightPix = 1080  # screen height in px
    monitorwidth = 54.3  # monitor width in cm
    viewdist = 60.  # viewing distance in cm
    monitorname = 'Screen_0'
    scrn = 0
    
    mon = monitors.Monitor(monitorname, width=monitorwidth, distance=viewdist)
    mon.setSizePix((widthPix, heightPix))

    win = visual.Window(fullscr=True, size=(widthPix, heightPix), color="grey",
                        units='pix', monitor=mon, pos=(0, -0.2), screen=scrn,
                        winType="pyglet")

    if check_os() in ['Linux']:
        kb = keyboard.Keyboard(device=-1)
    elif check_os() in ['Windows', 'macOS']:
        # kb = None
        kb = keyboard.Keyboard()
    # emoKeys = ['space', 'q']
    emoKeys = ['space', 'q']
    presented_audio_paths = []

    ##### Show instructions #####
    image_dir = op.join(data_dir, 'img_instructions')

    # Define images paths
    instr0_path = op.join(image_dir, 'recall_pseudo.png')
    instr1_path = op.join(image_dir, 'recall_pseudo_2.png')
    end_path = op.join(image_dir, 'end.png')
    slide_instr = visual.ImageStim(win, image=instr0_path, units="pix", 
                                   pos=(0, 0))
    slide_instr1 = visual.ImageStim(win, image=instr1_path, units="pix", 
                                    pos=(0, 0))
    slide_end = visual.ImageStim(win, image=end_path, units="pix", 
                                 pos=(0, 0))
    fixcross = visual.TextStim(win, text="+", units="norm", 
                               pos=(0, 0), color="black")
    fixcross_w = visual.TextStim(win, text="+", units="norm", 
                               pos=(0, 0), color="white")

    # Set audio recording
    cdate = datetime.now().strftime("%d%m%Y")
    ctime = datetime.now().strftime("%H%M%S")
    fs = 44100 
    recorded_data = []

    show(slide_instr)
    wait_kbd_emo(kb)
    show(slide_instr1)
    # wait_kbd_emo(kb)

    _audio_paths = audio_paths.copy()
    _sounds = sounds.copy()
    
    for n in range(99):
        if len(_sounds) == 0:
            _audio_paths = audio_paths.copy()
            _sounds = sounds.copy()
        pp = np.random.choice(len(_audio_paths))
        audio_path_presented = _audio_paths.pop(pp)
        sound_presented = _sounds.pop(pp)
        
        show(fixcross)
        core.wait(1.)
        send_trigger_thread(p, SN_TRIG)
        qst = np.full((sound_presented.shape[0], 1), np.nan)
        sd.playrec(sound_presented, samplerate=fs, channels=1, 
                   dtype='int16', out=qst, input_mapping=np.array([1]),
                   output_mapping=np.array([1, 2]))
        answ = np.full((60*45*fs, 1), np.nan)
        sd.wait()
        recorded_data.append(qst)
        sd.rec(samplerate=fs, channels=1, out=answ, dtype='int16')
        
        # Salva il percorso dell'audio presentato
        presented_audio_paths.append(audio_path_presented.split(os.sep)[-1])

        # Aspetta un input da tastiera e interrompi se premuto 'q'
        response = wait_kbd_emo(kb, okKeys=emoKeys, maxWait=18)
        
        # Flash a white cross before passing to the next pseudoword
        show(fixcross_w)
        core.wait(.25)
        win.flip()
        core.wait(.25)
        show(fixcross_w)
        core.wait(1.5)
        
        recorded_data.append(np.expand_dims(answ[~np.isnan(answ)], 1))
        
        if response is not None:
            if response.name == 'q':
                break
        
    # Salva la registrazione audio su file
    recorded_data = np.vstack(recorded_data)
    audio_file = save_recording_audio(recorded_data, output_directory, 
                                      subject_id, session, cdate, ctime, fs)

    # Salva i percorsi delle pseudoparole presentate in un CSV
    pd.DataFrame({'Presented_Audio': presented_audio_paths}).to_csv(
        op.join(output_directory, f'RY{subject_id:03d}_N{session}.csv'), 
        index=False)
    
    show(slide_end)
    core.wait(2)
    win.close()
    # --------------------------  EXPERIMENT END  --------------------------


if __name__ == "__main__":
    task_D()