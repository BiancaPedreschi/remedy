from utils.common_functions import check_os
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
from config.config import read_config
import os
import os.path as op
import time
import pandas as pd
from utils.common_functions import wait_kbd_emo, get_meta, show, str2num
from utils.find_serial import find_serial_device
from psychopy import visual, core, event, monitors
from psychopy.hardware import keyboard
from olfactometer_controller import olfactometer


config = read_config()
parent_dir = config['paths']['parent']
manualcomm_path = op.join(parent_dir, 'combinations', 'manual_commands.csv')
manualcomm_df = pd.read_csv(manualcomm_path, sep=';')

odorList = []

outputname = get_meta()
subject_id = outputname[0]
session = int(outputname[1])

data_dir = config['paths']['data']

participant_current_combinations = manualcomm_df[
    (manualcomm_df['Participant_ID'] == subject_id) & 
    (manualcomm_df['Session'] == session)]

odor_command_map = {}

# Itera sul dataframe dei comandi manuali
for index, row in participant_current_combinations.iterrows():
    odor = row['Odor']
    command = row['Command']
    odor_command_map[odor] = command
print(odor_command_map)

odorList = list(odor_command_map.keys())
commandList = list(odor_command_map.values())
print(commandList)

# _______________ OLFACTOMETER recalls

# port = "/dev/cu.usbmodem20220051"
# port = "/dev/ttyACM0"
# TODO: test this:
device_signature = 'f331:0002'
port = find_serial_device(device_signature)


output_directory = op.join(parent_dir, 'data', 'output_wake')
os.makedirs(output_directory, exist_ok=True)
current_day = time.strftime('%d%m%Y')
output_filename = f'stream_stimolf_Pp{subject_id}_sess{session}_{current_day}.txt'
output_file_path = os.path.join(output_directory, output_filename)

monitor = olfactometer(output_file_path)
monitor.set_serial(port=port)
monitor.open()
# ________________-   HARDWARE PARAMETER -

widthPix = 1920  # screen width in px
heightPix = 1080  # screen height in px
monitorwidth = 54.3  # monitor width in cm
viewdist = 60.  # viewing distance in cm
# monitorname = 'CH7210'
monitorname = 'DP-6'
scrn = 0  # 0 to use main screen, 1 to use external screen
mon = monitors.Monitor(monitorname, width=monitorwidth, distance=viewdist)
mon.setSizePix((widthPix, heightPix))

win = visual.Window(fullscr=True, size=(widthPix, heightPix), color="grey", 
                    units='pix', monitor=mon, pos=(0, -0.2), screen=scrn,
                    winType="pyglet") 

kb = keyboard.Keyboard(device=-1)
emoKeys = ['1','num_1','2','num_2','3','num_3','4','num_4','5','num_5','escape']

# ________________ -  INSTRUCTIONS   -
image_dir = op.join(data_dir, 'img_instructions')

# Percorsi completi per le immagini
instr1_path = op.join(image_dir, 'instr1_od.png')
end_path = op.join(image_dir, 'end.png')
instr2_path = op.join(image_dir, 'instr2.png')
instr3_path = op.join(image_dir, 'instr3.png')
valSAM_path = op.join(image_dir, 'valSAM.png')
aroSAM_path = op.join(image_dir, 'aroSAM.png')
slideBrk_path = op.join(image_dir, 'break.png')

slide_instr = visual.ImageStim(win, image=instr1_path, units="pix", pos=(0, 0))
slideBrk = visual.ImageStim(win, image=slideBrk_path, units="pix", pos=(0, 0))
slide_end = visual.ImageStim(win, image=end_path, units="pix", pos=(0, 0))
instrValSAM = visual.ImageStim(win, image=instr2_path, units="pix", pos=(0, 0))
instrAroSAM = visual.ImageStim(win, image=instr3_path, units="pix", pos=(0, 0))

# Fixation cross
fixcross = visual.TextStim(win, text="+", units="norm", pos=(0, 0.2), color="black")
valSAM = visual.ImageStim(win, image=valSAM_path, units="norm", pos=(0, 0))
aroSAM = visual.ImageStim(win, image=aroSAM_path, units="norm", pos=(0, 0))

names = [0] * len(odorList)
vals = [0] * len(odorList)
aros = [0] * len(odorList)
commands = [0] * len(commandList)

# --------------------------  INSTRUCTIONS  --------------------------

show(slide_instr)
wait_kbd_emo(kb)

show(instrValSAM)
wait_kbd_emo(kb)

show(instrAroSAM)
wait_kbd_emo(kb)


# --------------------------  EXPERIMENT START  --------------------------
def save_emotion_scores(names, vals, aros, commands):
    
    print(names)
    print(vals)
    print(aros)
    print(commands)

    df = pd.DataFrame({
        'Odor': names,
        'Valence': vals,
        'Arousal': aros,
        'Commands': commands
    })

    df.to_csv(op.join(output_directory, 
                      f"ODOR_EMO_SCORING_Pp{subject_id}_s_{session}.csv"), 
              index=False)


def handle_online_olf_shutdown(monitor, check_only=False):
    """
    Controlla se l'utente ha premuto 'q' per chiudere l'olfattometro in modo sicuro.
    Se check_only è True, controlla solo se è stato premuto 'q' senza chiudere nulla.
    Altrimenti, chiude tutto in modo sicuro.
    """
    if check_only:
        return  # Non fare nulla, solo il controllo è gestito nel ciclo principale

    key = event.getKeys()
    if 'q' in key:
        try:
            monitor.write('S 0')
            core.wait(3)
            print("interruzione manuale eseguita")
        except Exception as e:
            print(f"Errore durante la chiusura dell'olfattometro: {e}")
        finally:
              return True

def main(monitor):

    # Configurazione iniziale dell'olfattometro
    monitor.run()
    monitor.write('C M;;;;;;;')
    core.wait(0.5)
    monitor.write('E 1')
    core.wait(0.5)
    monitor.write('S 0')
    core.wait(5)

    counter = 0

    for nOdor, odor in enumerate(odorList):
        # Controlla se l'utente ha premuto 'q' ad ogni iterazione
        if handle_online_olf_shutdown(monitor,
                                   check_only=False):
            break

        # Esegue l'esperimento per ogni odore
        show(fixcross)
        core.wait(1)
        slide_odor = visual.TextStim(win, text=f"ODOR {nOdor + 1}", 
                                     units="norm", pos=(0, 0), color="black")

        names[nOdor] = odor
        show(slide_odor)
        monitor.write(commandList[nOdor])
        core.wait(5)

        commands[nOdor] = commandList[nOdor]

        # Valence rating
        valSAM.draw()
        win.flip()
        vals[nOdor] = str2num(wait_kbd_emo(kb, okKeys=emoKeys))

        # Arousal rating
        aroSAM.draw()
        win.flip()
        aros[nOdor] = str2num(wait_kbd_emo(kb, okKeys=emoKeys))

        show(fixcross)
        monitor.write('S 0')
        core.wait(10)

        counter += 1

    show(slide_end)
    core.wait(2)
    show(fixcross)
    core.wait(2)
    win.close()

    monitor.write('E 0')
    core.wait(0.5)
    monitor.stop()
    core.wait(0.5)
    monitor.close()

    save_emotion_scores(names, vals, aros, commands)


    # --------------------------  EXPERIMENT END  --------------------------


if __name__ == "__main__":
    main(monitor)

