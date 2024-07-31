from utils.common_functions import check_os
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
from utils.common_functions import get_meta_night
from config.config import read_config
from questionnaire.dreamquestrc import dreamquestrc
import os
import time
import pandas as pd
from psychopy import core, sound
import threading
from psychopy.hardware import keyboard
from datetime import datetime, timedelta
import random

def get_sound_name(sound_object):
    """Funzione per ottenere il nome del file audio da un oggetto Sound."""
    if hasattr(sound_object, 'name'):
        return sound_object.name
    elif hasattr(sound_object, 'filename'):
        return sound_object.filename
    else:
        return "Nome del suono non disponibile"
    
def main():
    config = read_config()
    parent_dir = config['paths']['parent']
    
    outputname = get_meta_night()
    participant_id = outputname[0]
    session = int(outputname[1])
    sex = outputname[2]

    # Carica le combinazioni di pseudoparole
    all_combinations_path = os.path.join(parent_dir, 'combinations', 'all_combinations_pseudo_simvid.csv')
    all_combinations_df = pd.read_csv(all_combinations_path)

    # Filtra il DataFrame per participant_id e session
    filtered_df = all_combinations_df[(all_combinations_df['Participant_ID'] == participant_id) & 
                                      (all_combinations_df['Session'] == session)]
    
    # Ottieni i percorsi delle pseudoparole
    audio_paths = filtered_df['Pseudo'].tolist()

    # Carica i suoni
    sounds = [sound.Sound(audio) for audio in audio_paths]

    # Imposta l'allarme
    alarm_path = os.path.join(parent_dir, 'alarm_beep.wav')
    alarm = sound.Sound(alarm_path)

    # Directory di output per i questionari sui sogni
    output_directory = os.path.join(parent_dir, 'output_NightStim')
    os.makedirs(output_directory, exist_ok=True)

    # Inizializza la tastiera
    kb = keyboard.Keyboard()

    def manual_stim():
        interrupted = False
        stimulation_started = False
        start_time = None
        min_duration = timedelta(minutes=1)
        max_duration = timedelta(minutes=12)

        def check_for_input():
            nonlocal interrupted, stimulation_started, start_time
            while True:
                keys = kb.getKeys(['q', 'r', 'space'])
                if 'q' in keys and stimulation_started:
                    print("Stimolazione interrotta. Premi la barra spaziatrice per ricominciare.")
                    interrupted = True
                    stimulation_started = False
                    start_time = None
                elif 'r' in keys and stimulation_started:
                    current_time = datetime.now()
                    if start_time and (current_time - start_time) >= min_duration:
                        print("Richiesta di terminare la stimolazione.")
                        interrupted = True
                    else:
                        print("Non puoi terminare la stimolazione prima di 5 minuti.")
                elif 'space' in keys and not stimulation_started:
                    stimulation_started = True
                    start_time = datetime.now()
                    print("Stimolazione iniziata.")
                core.wait(0.1)

        input_thread = threading.Thread(target=check_for_input)
        input_thread.start()
        while True:
            if not stimulation_started:
                print("Premi la barra spaziatrice per iniziare la stimolazione.")
                kb.waitKeys(keyList=['space'])
                stimulation_started = True
                start_time = datetime.now()
                selected_sound = random.choice(sounds)
                print(f"Suono selezionato: {get_sound_name(selected_sound)}")

            while stimulation_started:
                current_time = datetime.now()
                if start_time and (current_time - start_time) >= max_duration:
                    print("Durata massima raggiunta.")
                    interrupted = True
                    break

                if interrupted:
                    break

                selected_sound.play()
                core.wait(selected_sound.getDuration())
                if interrupted:
                    break
                core.wait(random.uniform(1.5, 2.5))

            if interrupted:
                core.wait(3)
                if start_time and (current_time - start_time) >= min_duration:
                    print("Riproducendo l'allarme.")
                    alarm.play()
                    kb.waitKeys(keyList=['space'])
                    print("Avvio del questionario...")
                    dreamquestrc(participant_id, session, sex, output_directory, fs=48000)
                    break
                else:
                    interrupted = False
                    stimulation_started = False

        input_thread.join()

    # Avvia la stimolazione manuale
    manual_stim()

if __name__ == "__main__":
    main()