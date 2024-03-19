from olfactometer_controller_B import olfactometer
from utils.common_functions import get_meta_night
import questionnaire.dreamquestrc
import os
import time
import psychtoolbox as ptb
from psychopy import core
import threading

outputlog = []
get_meta_night(outputlog)

participant_id = outputlog[0]
session = int(outputlog[1])
sex = outputlog[2]

# _______________ OLFACTOMETER inizialiation and output

port = "/dev/cu.usbmodem20220051"


output_directory = '/Users/foscagiannotti/Desktop/project_remedy/output_olfactometer'
current_day = time.strftime('%d%m%Y')
output_filename = f'Night Stimulation_Pp{participant_id}_session{session}_{current_day}'
output_file_path = os.path.join(output_directory, output_filename)

monitor = olfactometer(output_file_path)
monitor.set_serial(port=port)
monitor.open()

# Configurazione iniziale dell'olfattometro
monitor.run()
monitor.write('C M;;;;;;;')
core.wait(0.5)
monitor.write('E 1')
core.wait(0.5)
monitor.write('S 0')
core.wait(5)

# ________________Setting Alarm

AlarmName = 'alarm_beep48.wav'
myPath = '/Users/foscagiannotti/Desktop/project_remedy/'
fs_alarm, alarm = ptb.audioread(myPath + AlarmName)
myAlarm = ptb.LoadSound(alarm, 44100)

#__________________Outputdirectory of DreamQuestionnaires
mydir = os.getcwd()
output_directory = os.path.join(mydir, 'output_NightStim')

#________________Olfactometer Night Mode + Alarm + safe quit

def manual_stim():

    # Variabile globale per controllare l'interruzione
    interrupted = False

    def check_for_quit():
        global interrupted
        while not interrupted:
            if ptb.KeyPressed('q'):
                interrupted = True
                break
            core.wait(1)  # Controlla ogni secondo per ridurre il carico sul processore


    # Crea e avvia il thread per monitorare l'interruzione
    quit_thread = threading.Thread(target=check_for_quit)
    quit_thread.start()
    key = None

    if key in ['1', '2']:
        # Inizia la stimolazione basata su quale tasto è stato premuto
        for cycle in range(15):
            if interrupted:
                break  # Esce dal ciclo se è stata rilevata un'interruzione

            monitor.write(f'S {key}')
            core.wait(10)  # Tempo di stimolazione
            if interrupted:
                break # Esce dal ciclo se è stata rilevata un'interruzione

            monitor.write('S 0')
            core.wait(10)  # Tempo di pausa

# Assicurati di interrompere il thread una volta completato il ciclo
    interrupted = True
    quit_thread.join()

    if not interrupted:
        # Se la stimolazione arriva a compimento senza interruzioni, suona la sveglia
        ptb.PlaySound(myAlarm, fs_alarm)
        # Attende che io prema 'space' per avviare il questionario
        key = ptb.WaitKeyPress(['space'])
        if key == 'space':
            questionnaire.dreamquestrc(participant_id, session, sex, output_directory, fs=48000)
    monitor.write('S 0')

