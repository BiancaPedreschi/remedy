import threading  
from utils.common_functions import check_os
from utils.audio_recorder import start_recording, save_recording
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
from config.config import read_config
import os
import random
import os.path as op
import pandas as pd
from utils.common_functions import wait_kbd_emo, get_meta, show, str2num
from psychopy import visual, core, event, monitors, sound
from psychopy.hardware import keyboard

def main():
    config = read_config()
    parent_dir = config['paths']['parent']
    data_dir = op.join(parent_dir, 'data', 'remedy_data')
    all_combinations_path =  op.join(parent_dir, 'combinations', 
                                     'all_combinations_pseudo_simvid.csv')
    all_combinations_df = pd.read_csv(all_combinations_path)

    outputname = get_meta()
    subject_id = outputname[0]
    session = int(outputname[1])

    # Filtra il DataFrame per subject_id e session
    filtered_df = all_combinations_df[(all_combinations_df['Participant_ID'] == subject_id) & 
                                      (all_combinations_df['Session'] == session)]
    
    # Ottieni i percorsi delle pseudoparole
    audio_paths = filtered_df['Pseudo'].tolist() * 34  # Moltiplica per 34 per includere la ripetizione
    random.shuffle(audio_paths) 

    output_directory = op.join(parent_dir, 'data', 'output_wake')
    os.makedirs(output_directory, exist_ok=True)

    sounds = [sound.Sound(audio) for audio in audio_paths]  

    # widthPix = 1920  # screen width in px
    # heightPix = 1080  # screen height in px
    # monitorwidth = 54.3  # monitor width in cm
    # viewdist = 60.  # viewing distance in cm
    # monitorname = 'CH7210'
    #monitorname = 'DP-6'
    widthPix = 2560  # screen width in px
    heightPix = 1440  # screen height in px
    monitorwidth = 28.04  # monitor width in cm (puoi mantenere questo valore se è corretto)
    viewdist = 60.  # viewing distance in cm (puoi mantenere questo valore se è corretto)
    monitorname = 'MacBook Pro 13"'
    scrn = 0  # 0 to use main screen, 1 to use external screen
    mon = monitors.Monitor(monitorname, width=monitorwidth, distance=viewdist)
    mon.setSizePix((widthPix, heightPix))

    win = visual.Window(fullscr=True, size=(widthPix, heightPix), color="grey",
                        units='pix', monitor=mon, pos=(0, -0.2), screen=scrn,
                        winType="pyglet", allowGUI=False, waitBlanking=False)

    if check_os() in ['Linux']:
        kb = keyboard.Keyboard(device=-1)
    elif check_os() in ['Windows', 'macOS']:
        kb = None
    emoKeys = ['space', '5']
    presented_audio_paths = []

    # ________________ -  INSTRUCTIONS   -
    image_dir = op.join(data_dir, 'img_instructions')

    # Percorsi completi per le immagini
    instr0_path = op.join(image_dir, 'recall_pseudo.png')
    end_path = op.join(image_dir, 'end.png')
    slide_instr = visual.ImageStim(win, image=instr0_path, units="pix", pos=(0, 0))
    slide_end = visual.ImageStim(win, image=end_path, units="pix", pos=(0, 0))
    fixcross = visual.TextStim(win, text="+", units="norm", pos=(0, 0), color="black")

    # Configura la registrazione audio
    duration = 3600 
    fs = 44100 
    device_index = 0  # Assicurati che questo sia l'indice corretto
    recorded_data = []

    show(slide_instr)
    wait_kbd_emo(kb)

    stop_recording_event = threading.Event()
    recording_thread = threading.Thread(target=start_recording, args=(duration, fs, 2, stop_recording_event, recorded_data, device_index))
    recording_thread.start()  

    for n in range(len(audio_paths)):
        show(fixcross)
        core.wait(1.)
        sounds[n].play()
        core.wait(sounds[n].getDuration())
        sounds[n].stop()

        # Salva il percorso dell'audio presentato
        presented_audio_paths.append(audio_paths[n])

        # Aspetta un input da tastiera e interrompi se premuto '5'
        response = wait_kbd_emo(kb, okKeys=emoKeys)
        if '5' in response:
            stop_recording_event.set()  # Imposta l'evento per fermare la registrazione
            break
    stop_recording_event.set()
    recording_thread.join()

    # Salva i percorsi delle pseudoparole presentate in un CSV
    pd.DataFrame({'Presented_Audio_Paths': presented_audio_paths}).to_csv(
        op.join(output_directory, f"presented_audio_paths_{subject_id}_{session}.csv"), index=False)
    
    # Salva la registrazione audio su file
    if recorded_data:
        save_recording(recorded_data[0], output_directory, subject_id, session, fs)
    show(slide_end)
    core.wait(2)
    win.close()

    # --------------------------  EXPERIMENT END  --------------------------

if __name__ == "__main__":
    main()