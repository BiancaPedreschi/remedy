from remedy.utils.common_functions import check_os, get_meta_night
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
from psychopy import visual, core
from psychopy.hardware import keyboard
from psychopy import prefs

import numpy as np
import os
import pandas as pd
import random
import sounddevice as sd
import scipy.io.wavfile as sw
import parallel
import time
import threading

from remedy.config.config import read_config
from remedy.questionnaire.dreamquestrc import dreamquestrc
from remedy.utils.find_devices import find_device


prefs.hardware['audioLib'] = ['sounddevice', 'pyo', 'pygame', 'PTB']
prefs.hardware['audioDevice'] = 'sysdefault'
prefs.hardware['audioLatencyMode'] = 3

def send_trigger_thread(p, code, numlns=8):
    """
    Sends a trigger code converted to binary via serial port in a separate thread.

    Args:
        p : porta parallela
        code (int): The numeric code to send.
        numlns (int, optional): The number of lines (or pins)
        to use for the binary representation of the code. Default is 8.

    Returns:
        None
    """
    def trigger():
        print(f"Trigger inviato: {code}, binario: {code}")
        p.setData(code)
        time.sleep(0.01)
        p.setData(0)
    
    threading.Thread(target=trigger).start()
    return

    
def start_eeg_recording(p):
    RC_TRIG = 10  # Start Recording
    print("Avvio registrazione EEG")
    # send_trigger_thread(p=p, code=RC_TRIG)


def stop_eeg_recording(p):
    ED_TRIG = 40  # Stop Experiment
    print("Arresto registrazione EEG")
    # send_trigger_thread(p=p, code=ED_TRIG)


def select_stimuli(audio_paths):
    selected = random.sample(audio_paths, 2)
    control = [path for path in audio_paths if path not in selected][0]
    return selected[0], selected[1], control


def play_pink_noise(pink_noise):
    sd.play(pink_noise, loop=True)
    return pink_noise


def stop_pink_noise(pink_noise):
    sd.stop()
    return pink_noise


# def manual_stim(p, win, kb, subject_id, session, sex, n2_stimulus,
#                 rem_stimulus, pink_noise, dev_hp, dev_sp, stim_n):
def manual_stim(win, kb, subject_id, session, sex, n2_stimulus,
                rem_stimulus, pink_noise, stim_n):
    
    # Definizione dei codici trigger
    REM_TRIG = 22 # REM Stimulation
    N2_TRIG = 24 # N2 
    S_TRIG = 26  # Sham Stimulation
    AS_TRIG = 28  # Alarm Sound

    config = read_config()
    data_dir = config['paths']['data']
    results_dir = config['paths']['results']

    # Imposta l'allarme
    alarm_path = os.path.join(data_dir, 'alarm_beep.wav')

    output_directory = os.path.join(results_dir, f'RY{subject_id:03d}', 
                                    f'N{session}', 'task_E')
    os.makedirs(output_directory, exist_ok=True)

    stimulation_started = False
    min_duration = 5 #* 60 # da modificare fino a min di 5 minuti
    max_duration = 15 * 60

    timer_text = visual.TextStim(win, text='', pos=(0, 0.8), height=0.05)
    instruction_text = visual.TextStim(win, text='', pos=(0, 0), height=0.05)

    stimulation_timer = core.Clock()
    total_stim_timer = core.Clock()
    next_sound_time = 0
    selected_sound = None

    stimulation_times = []
    output_file = os.path.join(output_directory, 
                               f'RY{subject_id:03d}_N{session}_{stim_n}.csv')

    while True:

        if not stimulation_started:
            instruction_text.text = "Premi 'N' per stimolo N2, 'W' per stimolo REM, 'S' per Sham"
            instruction_text.draw()
            win.flip()
            keys = kb.waitKeys(keyList=['n', 'w', 's', 'escape', 'esc'])
            if 'escape' in keys or 'esc' in keys:
                return "quit"
            if 'n' in keys:
                stimulation_started = True
                n2_sound = sw.read(n2_stimulus)[1]
                selected_sound = n2_sound
                selected_sound_path = n2_stimulus
                print("Stimolazione N2 selezionata")
            elif 'w' in keys:
                stimulation_started = True
                rem_sound = sw.read(rem_stimulus)[1]
                selected_sound = rem_sound
                selected_sound_path = rem_stimulus
                print("Stimolazione REM selezionata")
            elif 's' in keys:
                stimulation_started = True
                selected_sound = None
                print("SHAM!")

            if stimulation_started:
                total_stim_timer.reset()
                stimulation_timer.reset()
                current_time = stimulation_timer.getTime()
                inter_stimulus_interval = random.uniform(1.5, 2.5)
                next_sound_time = current_time + inter_stimulus_interval

        if stimulation_started:
            elapsed_time = total_stim_timer.getTime()
            timer_text.text = f"Tempo trascorso: {elapsed_time:.0f} secondi"
            timer_text.draw()
            instruction_text.text = "Premi 'Q' per interrompere, 'R' per far partire la sveglia. "
            instruction_text.draw()
            win.flip()

            if elapsed_time >= max_duration:
                print("Durata massima raggiunta.")
                break
            
            keys = kb.getKeys(['q', 'r', 'escape', 'esc'])
            if 'escape' in keys or 'esc' in keys:
                return "quit"
            if 'q' in keys:
                print("Stimolazione interrotta. Tornando alla selezione dello stimolo.")
                stimulation_started = False
                stimulation_times = []
                stimulation_timer.reset()
                print(stimulation_timer.getTime())
                continue  # Torna all'inizio del ciclo while
            elif 'r' in keys:
                if elapsed_time >= min_duration:
                    print("Richiesta di terminare la stimolazione.")
                    break
                else:
                    print(f"Non puoi terminare la stimolazione prima di {min_duration} secondi.")

            # Nel ciclo principale:
            current_time = stimulation_timer.getTime()
            if current_time >= next_sound_time:
                if selected_sound is None:
                    # send_trigger_thread(p, S_TRIG)  # Invia il trigger S_TRIG per Sham
                    core.wait(1)
                else:
                    stop_pink_noise(pink_noise)
                    
                    # if np.all(selected_sound_path == n2_stimulus):
                    #     send_trigger_thread(p, N2_TRIG)  # Invia il trigger N2_TRIG
                    # elif np.all(selected_sound_path == rem_stimulus):
                    #     send_trigger_thread(p, REM_TRIG)  # Invia il trigger REM_TRIG
                    
                    sd.play(selected_sound)
                    stim_start_time = current_time
                    stimulation_times.append([stim_start_time, 
                                            selected_sound_path.split(
                                                os.sep)[-1]])
                    
                    print(f"Tempo atteso: {inter_stimulus_interval:.2f} secondi")
                    
                    sd.wait()
                    play_pink_noise(pink_noise)
                    
                # Aggiorna il tempo per il prossimo stimolo
                stimulation_timer.reset()
                current_time = stimulation_timer.getTime()
                inter_stimulus_interval = random.uniform(1.5, 2.5)
                next_sound_time = current_time + inter_stimulus_interval

            core.wait(0.01)

    # Salva i tempi di stimolazione
    df = pd.DataFrame(stimulation_times, columns=['Timestamp', 'Stimulus'])
    df.to_csv(output_file, index=False)

    # Codice per l'allarme e il questionario
    if stimulation_started:
        stop_pink_noise(pink_noise)
        instruction_text.text = "Riproduco l'allarme."
        instruction_text.draw()
        win.flip()
        # sd.default.device = dev_sp
        # send_trigger_thread(p, AS_TRIG)
        alarm = sw.read(alarm_path)[1]
        sd.play(alarm)
        core.wait(2)
        instruction_text.text = "Premi la barra spaziatrice per l'avvio del questionario..."
        instruction_text.draw()
        win.flip()
        kb.waitKeys(keyList=['space'])
        instruction_text.text = "Avvio del questionario..."
        instruction_text.draw()
        win.flip()    
        dreamquestrc(subject_id, session, sex, fs=44100)
        # sd.default.device = dev_hp

    return "continue"


def task_E():
    
    # if check_os() in ['Linux']:
    #     kb = keyboard.Keyboard(device=-1)
    # elif check_os() in ['Windows', 'macOS']:
    #     kb = None
    if check_os() in ['Linux', 'Windows', 'macOS']:
        kb = keyboard.Keyboard(device=-1)
    else:
        kb = None
    # dev_hp, dev_sp = find_device()
    # sd.default.device = dev_hp
    
    win = visual.Window(fullscr=False, color="black", units="norm")
    instruction_text = visual.TextStim(win, text='', pos=(0, 0), height=0.05)
    
    # Inizializzazione della porta parallela LPT1
    # try:
    #     p = parallel.Parallel()
    #     print("Porta parallela aperta")
    # except Exception as e:
    #     p = None
    #     print("Errore apertura porta parallela")
    
    # Define triggers
    BG_TRIG = 20 # Start Experiment
    I_TRIG = 30 # Interruption
    
    # Uncomment if you want to automatically start EEG recording
    # start_eeg_recording(p)

    # Ottieni le informazioni una sola volta all'inizio
    outputname = get_meta_night()
    subject_id = outputname[0]
    session = int(outputname[1])
    sex = outputname[2]

    config = read_config()
    parent_dir = config['paths']['parent']
    data_dir = config['paths']['data']
    all_combinations_path = os.path.join(parent_dir, 'combinations', 
                                         'all_combinations_pseudo_night.csv')
    all_combinations_df = pd.read_csv(all_combinations_path)
    filtered_df = all_combinations_df[(all_combinations_df['Participant_ID'] == subject_id) & 
                                      (all_combinations_df['Session'] == session)]
    
    audio_paths = filtered_df['Pseudo'].tolist()
    n2_stimulus, rem_stimulus, control_stimulus = select_stimuli(audio_paths)

    print(f"Stimolo N2: {os.path.basename(n2_stimulus)}")
    print(f"Stimolo REM: {os.path.basename(rem_stimulus)}")
    print(f"Stimolo di controllo (non usato): {os.path.basename(control_stimulus)}")

    # Read the pink noise file
    pink_noise_file = os.path.join(parent_dir, 'data', 'pwd', 
                                   'night_stim', 'PN.wav')
    pink_noise = sw.read(pink_noise_file)[1]
    # send_trigger_thread(p, BG_TRIG)
    pink_noise = play_pink_noise(pink_noise)
    print("Pink noise avviato.")

    stimulation_count = 0
    max_stimulations = 16  # Numero massimo di stimolazioni prima di terminare

    try:
        while stimulation_count < max_stimulations:
            print(f"Iniziando stimolazione {stimulation_count + 1} di {max_stimulations}")
            # result = manual_stim(p=p, win=win, kb=kb, subject_id=subject_id,
            #                      session=session, sex=sex, 
            #                      n2_stimulus=n2_stimulus, 
            #                      rem_stimulus=rem_stimulus, 
            #                      pink_noise=pink_noise, 
            #                      dev_hp=dev_hp, dev_sp=dev_sp, 
            #                      stim_n=stimulation_count)
            result = manual_stim(win=win, kb=kb, subject_id=subject_id,
                                session=session, sex=sex, 
                                n2_stimulus=n2_stimulus, 
                                rem_stimulus=rem_stimulus, 
                                pink_noise=pink_noise,
                                stim_n=stimulation_count)        
        
            if result == "quit":
                instruction_text.text = "Uscita richiesta dall'utente."
                instruction_text.draw()
                win.flip()
                break
            elif result == "continue":
                stimulation_count += 1
                instruction_text.text = f"Stimolazione completata. Totale stimolazioni: {stimulation_count}"
                instruction_text.draw()
                win.flip()
                if stimulation_count < max_stimulations:
                    instruction_text.text = "Premi 'C' per continuare con la prossima stimolazione o 'Q' per terminare."
                    instruction_text.draw()
                    win.flip()
                    keys = kb.waitKeys(keyList=['c', 'q'])
                    if 'q' in keys:
                        instruction_text.text = "Uscita richiesta dall'utente."
                        instruction_text.draw()
                        win.flip()
                        break
                    stop_pink_noise(pink_noise)
                    pink_noise = play_pink_noise(pink_noise)

            else:
                instruction_text.text = f"Risultato inaspettato: {result}"
                instruction_text.draw()
                win.flip()
                break

        instruction_text.text = f"Esperimento completato dopo {stimulation_count} stimolazioni."
        instruction_text.draw()
        win.flip()
    finally:
        # send_trigger_thread(p, I_TRIG)
        stop_pink_noise(pink_noise)
        # Uncomment if you want to automatically stop EEG recording
        # stop_eeg_recording(p)
        win.close()

if __name__ == "__main__":
    task_E()