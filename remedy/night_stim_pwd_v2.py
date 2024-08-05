from utils.common_functions import check_os, get_meta_night
from config.config import read_config
from questionnaire.trout import trgout
from questionnaire.dreamquestrc import dreamquestrc
import os
import pandas as pd
import random
from psychopy import visual, core, sound, event
from psychopy import prefs

prefs.hardware['audioLib'] = ['ptb', 'pyo', 'pygame']
prefs.general['audioDevice'] = 'default'

if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()

# Definizione dei codici trigger
RC_TRIG = 10  # Start Recording
BG_TRIG = 20  # Start Experiment
AS_TRIG = 30  # Alarm Sound
ED_TRIG = 40  # Stop Experiment

def send_trigger(code, numlns=8):
    trigger_bin = trgout(code, numlns)
    print(f"Trigger inviato: {code}, binario: {trigger_bin}")

def select_stimuli(audio_paths):
    selected = random.sample(audio_paths, 2)
    control = [path for path in audio_paths if path not in selected][0]
    return selected[0], selected[1], control

def manual_stim(win, participant_id, session, sex):
    config = read_config()
    parent_dir = config['paths']['parent']

    all_combinations_path = os.path.join(parent_dir, 'combinations', 'all_combinations_pseudo_final.csv')
    all_combinations_df = pd.read_csv(all_combinations_path)
    filtered_df = all_combinations_df[(all_combinations_df['Participant_ID'] == participant_id) & 
                                      (all_combinations_df['Session'] == session)]
    
    audio_paths = filtered_df['Pseudo'].tolist()
    n2_stimulus, rem_stimulus, control_stimulus = select_stimuli(audio_paths)

    print(f"Stimolo N2: {os.path.basename(n2_stimulus)}")
    print(f"Stimolo REM: {os.path.basename(rem_stimulus)}")
    print(f"Stimolo di controllo (non usato): {os.path.basename(control_stimulus)}")

    # Carica i suoni
    n2_sound = sound.Sound(n2_stimulus)
    rem_sound = sound.Sound(rem_stimulus)

    # Imposta l'allarme
    alarm_path = os.path.join(parent_dir, 'alarm_beep.wav')
    alarm = sound.Sound(alarm_path)

    output_directory = os.path.join(parent_dir, 'output_NightStim')
    os.makedirs(output_directory, exist_ok=True)

    stimulation_started = False
    min_duration = 1 * 60
    max_duration = 12 * 60

    timer_text = visual.TextStim(win, text='', pos=(0, 0.8), height=0.05)
    instruction_text = visual.TextStim(win, text="Premi 'N' per stimolo N2, 'W' per stimolo REM", pos=(0, 0), height=0.05)

    clock = core.Clock()
    next_sound_time = 0
    selected_sound = None

    while True:
        current_time = clock.getTime()

        if not stimulation_started:
            instruction_text.draw()
            win.flip()
            keys = event.waitKeys(keyList=['n', 'w', 'escape'])
            if 'escape' in keys:
                return False
            if 'n' in keys:
                stimulation_started = True
                selected_sound = n2_sound
                print("Stimolazione N2 selezionata")
            elif 'w' in keys:
                stimulation_started = True
                selected_sound = rem_sound
                print("Stimolazione REM selezionata")

            if stimulation_started:
                clock.reset()
                send_trigger(BG_TRIG)
                print(f"File audio selezionato: {os.path.basename(selected_sound.fileName)}")


        if stimulation_started:
            elapsed_time = current_time
            timer_text.text = f"Tempo trascorso: {elapsed_time:.0f} secondi"
            timer_text.draw()
            instruction_text.text = "Premi 'Q' per interrompere, 'R' per far partire la sveglia. "
            instruction_text.draw()
            win.flip()

            if elapsed_time >= max_duration:
                print("Durata massima raggiunta.")
                break

            keys = event.getKeys(['q', 'r', 'escape'])
            if 'escape' in keys:
                send_trigger(ED_TRIG)   
                return "quit"
            if 'q' in keys:
                print("Stimolazione interrotta. Premi 'N' per N2 o 'W' per REM per ricominciare.")
                stimulation_started = False
                send_trigger(ED_TRIG)
                clock.reset()
            elif 'r' in keys:
                if elapsed_time >= min_duration:
                    print("Richiesta di terminare la stimolazione.")
                    send_trigger(ED_TRIG)
                    break
                else:
                    print("Non puoi terminare la stimolazione prima di 5 minuti.")

            if current_time >= next_sound_time:
                selected_sound = n2_sound #TODO: implementare logica di scelta n2/rem
                print(f"File audio selezionato: {os.path.basename(selected_sound.fileName)}")
                selected_sound.play()
                next_sound_time = current_time + selected_sound.getDuration() + random.uniform(1.5, 2.5)

        core.wait(0.1)

    # Codice per l'allarme e il questionario
    if stimulation_started:
        print("Riproducendo l'allarme.")
        send_trigger(AS_TRIG)
        alarm.play()
        core.wait(alarm.getDuration())
        print("Premi la barra spaziatrice per l'avvio del questionario...")
        event.waitKeys(keyList=['space'])
        print("Avvio del questionario...")
        dreamquestrc(participant_id, session, sex, output_directory, fs=48000)

    return "continue"

def start_eeg_recording():
    print("Avvio registrazione EEG")
    send_trigger(RC_TRIG)

def stop_eeg_recording():
    print("Arresto registrazione EEG e salvataggio dati")
    send_trigger(ED_TRIG)

def wait_for_next_stimulation(win):
    instruction = visual.TextStim(win, text="Attendi la prossima stimolazione. Premi 'S' quando sei pronto.", pos=(0, 0), height=0.05)
    instruction.draw()
    win.flip()
    core.wait(2)
    event.waitKeys(keyList=['s'])

def main():
    win = visual.Window(fullscr=False, color="black", units="norm")
    start_eeg_recording()

    # Ottieni le informazioni una sola volta all'inizio
    outputname = get_meta_night()
    participant_id = outputname[0]
    session = int(outputname[1])
    sex = outputname[2]

    stimulation_count = 0
    max_stimulations = 8  # Numero massimo di stimolazioni prima di terminare

    try:
        while stimulation_count < max_stimulations:
            print(f"Iniziando stimolazione {stimulation_count + 1} di {max_stimulations}")
            result = manual_stim(win, participant_id, session, sex)
            
            if result == "quit":
                print("Uscita richiesta dall'utente.")
                break
            elif result == "continue":
                stimulation_count += 1
                print(f"Stimolazione completata. Totale stimolazioni: {stimulation_count}")
                if stimulation_count < max_stimulations:
                    wait_for_next_stimulation(win)
            else:
                print(f"Risultato inaspettato: {result}")
                break

        print(f"Esperimento completato dopo {stimulation_count} stimolazioni.")
    finally:
        stop_eeg_recording()
        win.close()

if __name__ == "__main__":
    main()