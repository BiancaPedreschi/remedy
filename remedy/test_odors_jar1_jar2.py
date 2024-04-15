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
from utils.common_functions import wait_kbd_emo_and_get_time, wait_kbd_emo, get_meta_test_od, show, str2num_2
from utils.find_serial import find_serial_device
from psychopy import visual, core, event, monitors
from psychopy.hardware import keyboard
from olfactometer_controller import olfactometer

config = read_config()
parent_dir = config['paths']['parent']
manualcomm_path = op.join(parent_dir, 'combinations', 'manual_commands.csv')
manualcomm_df = pd.read_csv(manualcomm_path, sep=';')

outputname = get_meta_test_od()
subject_id = outputname[0]
odor1 = outputname[1]
odor2 = outputname[2]

data_dir = config['paths']['data']

odorList = ['Odore 1', 'Odore 2']
commandList = ['S 1', 'S 2']
namesList = [{odor1}, {odor2}]
# _______________ OLFACTOMETER recalls
########################################
# port = "/dev/cu.usbmodem20220051"
# port = "/dev/ttyACM0"


# device_signature = 'f331:0002'
# port = find_serial_device(device_signature)
#
output_directory = op.join(parent_dir, 'data', 'output_wake')
# os.makedirs(output_directory, exist_ok=True)
# current_day = time.strftime('%d%m%Y')
# output_filename = f'stream_stimolf_Pp{subject_id}_test{odor1, odor2}_{current_day}.txt'
# output_file_path = os.path.join(output_directory, output_filename)
#
# olfm = olfactometer(output_file_path)
# olfm.set_serial(port=port)
# olfm.open()
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

win = visual.Window(fullscr=False, size=(widthPix, heightPix), color="grey",
                    units='pix', monitor=mon, pos=(0, -0.2), screen=scrn,
                    winType="pyglet")

# if check_os() in ['Linux']:
#     kb = keyboard.Keyboard(device=-1)
# elif check_os() in ['Windows', 'macOS']:
#     kb = None

kb = None
emoKeys = ['1', 'num_1', '2', 'num_2', '3', 'num_3', '4', 'num_4', '5', 'num_5', 'escape']
timeKeys = ["space", "escape", "right"]

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
wait_kbd_emo_and_get_time(kb)

show(instrValSAM)
wait_kbd_emo_and_get_time(kb)

show(instrAroSAM)
wait_kbd_emo_and_get_time(kb)
show(fixcross)
win.flip()


# --------------------------  EXPERIMENT START  --------------------------
def save_emotion_scores(names, vals, aros, commands, space_press_times,
                        second_space_press_times):
    df = pd.DataFrame({
        'Odor': namesList,
        'Valence': vals,
        'Arousal': aros,
        'Commands': commandList,
        'FirstSpacePressTime': space_press_times,
        'SecondSpacePressTime': second_space_press_times
    })

    df.to_csv(op.join(output_directory,
                      f"ODORS_testing_Pp{subject_id}_{odor1}_{odor2}.csv"),
              index=False)
###########################

# def handle_online_olf_shutdown(monitor, check_only=False):
#     """
#     Controlla se l'utente ha premuto 'q' per chiudere l'olfattometro in modo sicuro.
#     Se check_only è True, controlla solo se è stato premuto 'q' senza chiudere nulla.
#     Altrimenti, chiude tutto in modo sicuro.
#     """
#     if check_only:
#         return  # Non fare nulla, solo il controllo è gestito nel ciclo principale
#
#     key = event.getKeys()
#     if 'q' in key:
#         try:
#             olfm.write('S 0')
#             core.wait(3)
#             print("interruzione manuale eseguita")
#         except Exception as e:
#             print(f"Errore durante la chiusura dell'olfattometro: {e}")
#         finally:
#             return True

def main():
    # Configurazione iniziale dell'olfattometro
    # olfm.run()
    # olfm.write('C M;;;;;;;')
    # core.wait(0.5)
    # olfm.write('E 1')
    # core.wait(0.5)
    # olfm.write('S 0')
    # core.wait(5)

    counter = 0
    space_press_times = []
    second_space_press_times = []


    for nOdor, command in enumerate(commandList):

        # Esegue l'esperimento per ogni odore
        show(fixcross)
        core.wait(1)
        slide_odor = visual.TextStim(win, text=f"ODOR {nOdor + 1}",
                                     units="norm", pos=(0, 0), color="black")

        slide_time1 = visual.TextStim(win, text=f"Premi la freccia destra"
                                                f" quando senti l'odore",
                                     units="norm", pos=(0, 0), color="black")
        slide_time2 = visual.TextStim(win, text=f"Premi la freccia destra "
                                                f"quando NON senti più l'odore",
                                      units="norm", pos=(0, 0), color="black")

        show(slide_odor)
        core.wait(3)

        #olfm.write(command)
        show(slide_time1)
        tempo_premuto1 = wait_kbd_emo_and_get_time(kb, okKeys=timeKeys)
        if tempo_premuto1 is not None:
            space_press_times.append(tempo_premuto1)
        show(fixcross)
        core.wait(4)

        #olfm.write('S 0')
        show(slide_time2)
        tempo_premuto2 = wait_kbd_emo_and_get_time(kb, okKeys=timeKeys)
        if tempo_premuto2 is not None:
            second_space_press_times.append(tempo_premuto2)
        show(fixcross)
        core.wait(4)


        # Valence rating
        valSAM.draw()
        win.flip()
        response = wait_kbd_emo_and_get_time(kb, okKeys=emoKeys)
        if response is not None:
            keyName, _ = response # Ignora il tempo di reazione
            vals[nOdor] = str2num_2(keyName)  # Passa solo il nome del tasto a str2num_2
        else:
            # Gestisci il caso in cui non viene premuto nessun tasto valido
            print("Nessun tasto valido premuto.")


        # Arousal rating
        aroSAM.draw()
        win.flip()
        response = wait_kbd_emo_and_get_time(kb, okKeys=emoKeys)
        if response is not None:
            keyName, _ = response  # Ignora il tempo di reazione
            aros[nOdor] = str2num_2(keyName)  # Passa solo il nome del tasto a str2num_2
        else:
            # Gestisci il caso in cui non viene premuto nessun tasto valido
            print("Nessun tasto valido premuto.")

        show(fixcross)
        #olfm.write('S 0')
        core.wait(2)


        counter += 1

    show(slide_end)
    core.wait(2)
    win.close()

    # olfm.write('E 0')
    # core.wait(0.5)
    # olfm.stop()
    # core.wait(0.5)
    # olfm.close()

    save_emotion_scores(names, vals, aros, commands,space_press_times,second_space_press_times)

    # --------------------------  EXPERIMENT END  --------------------------


if __name__ == "__main__":
    main()
    #main(olfm)

