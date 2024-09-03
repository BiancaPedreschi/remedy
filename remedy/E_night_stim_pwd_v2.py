from utils.common_functions import check_os, get_meta_night
from config.config import read_config
from questionnaire.trout import trgout
from questionnaire.dreamquestrc import dreamquestrc
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

# Inizializzazione della porta parallela
address = 0x3EFC
p = parallel.Parallel()

def send_trigger(code, numlns=8):
    """
        Invia un codice di trigger convertito in binario tramite porta seriale.

        Args:
            code (int): Il codice numerico da inviare.
            numlns (int, opzionale): Il numero di linee (o pin) da utilizzare
            per la rappresentazione binaria del codice. Default è 8.

        Returns:
            None
    """
    trigger_bin = trgout(code, numlns)
    print(f"Trigger inviato: {code}, binario: {trigger_bin}")
    # Converti la lista binaria in un numero decimale
    trigger_value = int(''.join(map(str, trigger_bin)), 2)
    
    # Invia il valore alla porta parallela, attende 10ms e poi resetta la porta
    p.setData(trigger_value)
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

def start_eeg_recording():
    print("Avvio registrazione EEG")
    send_trigger(RC_TRIG)

def stop_eeg_recording():
    print("Arresto registrazione EEG")
    send_trigger(ED_TRIG)

def select_stimuli(audio_paths):
    selected = random.sample(audio_paths, 2)
    control = [path for path in audio_paths if path not in selected][0]
    return selected[0], selected[1], control

def play_pink_noise(pink_noise_file):
    # sd.default.device = 0
    # pink_noise = sound.Sound(pink_noise_file, loops=-1)  # -1 per loop infinito
    pink_noise = sw.read(pink_noise_file)[1]
    sd.play(pink_noise, loop=True)
    # pink_noise.play()
    return pink_noise

def stop_pink_noise(pink_noise):
    # if pink_noise:
    sd.stop()
        # pink_noise.stop()
        # pink_noise = None
    return pink_noise

# def fade_sound(sound_obj, duration=0.1, fade_in=True, start_volume=0, end_volume=1):
#     steps = int(duration * 100) 
#     for i in range(steps):
#         if fade_in:
#             volume = start_volume + (end_volume - start_volume) * (i / (steps - 1))
#         else:
#             volume = end_volume - (end_volume - start_volume) * (i / (steps - 1))
#         sound_obj.setVolume(volume)
#         core.wait(duration / steps)


def manual_stim(win, participant_id, session, sex, n2_stimulus, rem_stimulus,
                 parent_dir, pink_noise):
    # Carica i suoni
    # n2_sound = sound.Sound(n2_stimulus)
    # rem_sound = sound.Sound(rem_stimulus)

    # Imposta l'allarme
    alarm_path = os.path.join(parent_dir, 'alarm_beep.wav')
    # alarm = sound.Sound(alarm_path)

    output_directory = os.path.join(parent_dir, 'output_NightStim')
    os.makedirs(output_directory, exist_ok=True)

    stimulation_started = False
    min_duration = 5  # da modificare fino a min di 5 minuti
    max_duration = 12 * 60

    timer_text = visual.TextStim(win, text='', pos=(0, 0.8), height=0.05)
    instruction_text = visual.TextStim(win, text='', pos=(0, 0), height=0.05)

    stimulation_timer = core.Clock()
    next_sound_time = 0
    selected_sound = None

    stimulation_times = []
    output_file = os.path.join(output_directory,
                                f"stim_times_{participant_id}_{session}.csv")

    # Avvia il pink noise a volume basso
    # pink_noise.setVolume(0.9)  # Volume iniziale basso
   
    

    while True:
        current_time = stimulation_timer.getTime()

        if not stimulation_started:
            instruction_text.text = "Premi 'N' per stimolo N2, 'W' per stimolo REM"
            instruction_text.draw()
            win.flip()
            # keys = event.waitKeys(keyList=['n', 'w', 'escape', 'esc'])
            keys = kb.waitKeys(keyList=['n', 'w', 'escape', 'esc'])
            if 'escape' in keys or 'esc' in keys:
                return "quit"
            if 'n' in keys:
                stimulation_started = True
                stop_pink_noise(pink_noise)
                n2_sound = sw.read(n2_stimulus)[1]
                selected_sound = n2_sound
                # n2_sound = sound.Sound(n2_stimulus)
                # selected_sound = n2_sound
                print("Stimolazione N2 selezionata")
            elif 'w' in keys:
                stimulation_started = True
                stop_pink_noise(pink_noise)
                rem_sound = sw.read(rem_stimulus)[1]
                selected_sound = rem_sound
                # rem_sound = sound.Sound(rem_stimulus)
                # selected_sound = rem_sound
                print("Stimolazione REM selezionata")

            if stimulation_started:
                stimulation_timer.reset()
                next_sound_time = 0  # Resetta il tempo per il prossimo suono
                send_trigger(A_TRIG)
                # stop_pink_noise(pink_noise)
                # print(f"File audio selezionato: {os.path.basename(selected_sound.fileName)}")

        if stimulation_started:
            # stop_pink_noise(pink_noise)
            elapsed_time = current_time
            timer_text.text = f"Tempo trascorso: {elapsed_time:.0f} secondi"
            timer_text.draw()
            instruction_text.text = "Premi 'Q' per interrompere, 'R' per far partire la sveglia. "
            instruction_text.draw()
            win.flip()

            if elapsed_time >= max_duration:
                print("Durata massima raggiunta.")
                break

            # keys = event.getKeys(['q', 'r', 'escape', 'esc'])
            keys = kb.getKeys(['q', 'r', 'escape', 'esc'])
            if 'escape' in keys or 'esc' in keys:
                stop_eeg_recording()
                return "quit"
            if 'q' in keys:
                print("Stimolazione interrotta. Tornando alla selezione dello stimolo.")
                stimulation_started = False
                stimulation_timer.reset()
                send_trigger(I_TRIG)
                print(stimulation_timer.getTime())
                continue  # Torna all'inizio del ciclo while
            elif 'r' in keys:
                if elapsed_time >= min_duration:
                    print("Richiesta di terminare la stimolazione.")
                    stop_pink_noise(pink_noise) 
                    send_trigger(I_TRIG)
                    break
                else:
                    print(f"Non puoi terminare la stimolazione prima di {min_duration} secondi.")

            # Nel ciclo principale:
            if current_time >= next_sound_time:
                # stop_pink_noise(pink_noise)
                # selected_sound.play()
                sd.play(selected_sound)
                stim_start_time = current_time
                # stim_duration = selected_sound.getDuration()
                # print(f"Durata stimolo: {stim_duration:.2f} secondi")  # Stampa la durata dello stimol
                # Calcola un intervallo casuale tra 1.5 e 2.5 secondi
                inter_stimulus_interval = random.uniform(1.5, 2.5)
                print(f"Tempo atteso: {inter_stimulus_interval:.2f} secondi")

                # Attendi l'intervallo tra gli stimoli
                core.wait(inter_stimulus_interval)

                # Aggiorna il tempo per il prossimo stimolo
                next_sound_time = stim_start_time + inter_stimulus_interval

            core.wait(0.01)

    # Salva i tempi di stimolazione
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp', 'Stimulus'])
        writer.writerows(stimulation_times)

    # Codice per l'allarme e il questionario
    if stimulation_started:
        stop_pink_noise(pink_noise)
        sd.default.device = 5
        print("Riproduco l'allarme.")
        send_trigger(AS_TRIG)
        alarm = sw.read(alarm_path)[1]
        sd.play(alarm)
        # alarm = sound.Sound(alarm_path)
        # alarm.play()
        core.wait(2) 
        # core.wait(alarm.getDuration())
        print("Premi la barra spaziatrice per l'avvio del questionario...")
        # event.waitKeys(keyList=['space'])
        kb.waitKeys(keyList=['space'])
        print("Avvio del questionario...")
        dreamquestrc(participant_id, session, sex, output_directory, fs=48000)
        sd.default.device = 0

    return "continue"


def main():
    
    # widthPix = 1920  # screen width in px
    # heightPix = 1080  # screen height in px
    # monitorwidth = 54.3  # monitor width in cm
    # viewdist = 60.  # viewing distance in cm
    # #monitorname = 'CH7210'
    # monitorname = 'DP-6'
    # # scrn = 1  # 0 to use main screen, 1 to use external screen
    # # widthPix = 2560  # screen width in px
    # # heightPix = 1440  # screen height in px
    # # monitorwidth = 28.04  # monitor width in cm (puoi mantenere questo valore se è corretto)
    # # viewdist = 60.  # viewing distance in cm (puoi mantenere questo valore se è corretto)
    # # monitorname = 'MacBook Pro 13"'
    # scrn = 0 
    # mon = monitors.Monitor(monitorname, width=monitorwidth, distance=viewdist)
    # mon.setSizePix((widthPix, heightPix))
    
    # win = visual.Window(fullscr=False, size=(widthPix, heightPix), color="grey",
    #                 units='pix', monitor=mon, pos=(0, -0.2), screen=scrn,
    #                 winType="pyglet")
    sd.default.device = 0
    
    win = visual.Window(fullscr=False, color="black", units="norm")
    start_eeg_recording()

    # Ottieni le informazioni una sola volta all'inizio
    outputname = get_meta_night()
    participant_id = outputname[0]
    session = int(outputname[1])
    sex = outputname[2]

    config = read_config()
    parent_dir = config['paths']['parent']
    all_combinations_path = os.path.join(parent_dir, 'combinations',
                                          'all_combinations_pseudo_final.csv')
    all_combinations_df = pd.read_csv(all_combinations_path)
    filtered_df = all_combinations_df[(all_combinations_df['Participant_ID'] == participant_id) & 
                                      (all_combinations_df['Session'] == session)]
    
    audio_paths = filtered_df['Pseudo'].tolist()
    n2_stimulus, rem_stimulus, control_stimulus = select_stimuli(audio_paths)

    print(f"Stimolo N2: {os.path.basename(n2_stimulus)}")
    print(f"Stimolo REM: {os.path.basename(rem_stimulus)}")
    print(f"Stimolo di controllo (non usato): {os.path.basename(control_stimulus)}")

    pink_noise_file = "pink_noise_60min.wav"
    pink_noise = play_pink_noise(pink_noise_file)
    print("Pink noise avviato.")
    send_trigger(BG_TRIG)


    stimulation_count = 0
    max_stimulations = 8  # Numero massimo di stimolazioni prima di terminare

    try:
        while stimulation_count < max_stimulations:
            print(f"Inizio stimolazione {stimulation_count + 1} di {max_stimulations}")
            result = manual_stim(win, participant_id, session, sex, n2_stimulus,
                                  rem_stimulus, parent_dir, pink_noise)
            
            if result == "quit":
                print("Uscita richiesta dall'utente.")
                break
            elif result == "continue":
                stimulation_count += 1
                print(f"Stimolazione completata. Totale stimolazioni: {stimulation_count}")
                if stimulation_count < max_stimulations:
                    print("Premi 'C' per continuare con la prossima stimolazione o 'Q' per terminare.")
                    # keys = event.waitKeys(keyList=['c', 'q'])
                    keys = kb.waitKeys(keyList=['c', 'q'])
                    if 'q' in keys:
                        print("Uscita richiesta dall'utente.")
                        break
                    stop_pink_noise(pink_noise)
                    pink_noise = play_pink_noise(pink_noise_file)

            else:
                print(f"Risultato inaspettato: {result}")
                break

        print(f"Esperimento completato dopo {stimulation_count} stimolazioni.")
    finally:
        stop_pink_noise(pink_noise)
        stop_eeg_recording()
        win.close()

if __name__ == "__main__":
    main()