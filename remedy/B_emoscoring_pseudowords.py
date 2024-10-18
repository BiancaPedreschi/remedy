from utils.common_functions import check_os
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
from remedy.config.config import read_config
import os
import os.path as op
import pandas as pd
from remedy.utils.common_functions import (wait_kbd_emo, get_meta, show, 
                                           send_trigger_thread)
from psychopy import visual, core, monitors
from psychopy.hardware import keyboard
from psychopy import prefs
from remedy.utils.find_devices import find_device
import soundfile as sf
import sounddevice as sd
import parallel


prefs.hardware['audioLib'] = ['ptb', 'pyo', 'pygame']
prefs.general['audioDevice'] = 'default'


def save_emotion_scores(names, vals, aros, output_directory, 
                        subject_id, session):
    df = pd.DataFrame({
        'Audio': names,
        'Valence': vals,
        'Arousal': aros,
    })
    df.to_csv(op.join(output_directory, f'RY{subject_id:03d}_N{session}.csv'), 
              index=False)
    return


def task_B():
    # Define audio devices and paths
    devices = find_device()
    dev_hp = devices[0]
    config = read_config()
    parent_dir = config['paths']['parent']
    data_dir = config['paths']['data']
    results_dir = config['paths']['results']
    
    all_combinations_path =  op.join(parent_dir, 'combinations', 
                                     'all_combinations_pseudo_day.csv')
    all_combinations_df = pd.read_csv(all_combinations_path)
    
    # Define parallel port
    try:
        p = parallel.Parallel()
        print("Porta parallela aperta")
    except Exception as e:
        p = None
        print("Errore apertura porta parallela")
    
    # Define trigger
    SN_TRIG = 26 # Trigger for sound presentation

    # Get subject data
    outputname = get_meta()
    subject_id = outputname[0]
    session = int(outputname[1])

    # Filter DataFrame by subject_id and session
    filtered_df = all_combinations_df[
        (all_combinations_df['Participant_ID'] == subject_id) & 
        (all_combinations_df['Session'] == session)
        ]
    
    # Get pseudowords audio paths
    audio_paths = filtered_df['Pseudo'].tolist()
    print(audio_paths)

    output_directory = op.join(results_dir, f'RY{subject_id:03d}', 
                               f'N{session}', 'task_B')
    os.makedirs(output_directory, exist_ok=True)
    sd.default.device = dev_hp
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
        kb = None
    emoKeys = ['1', 'num_1', '2', 'num_2', '3', 'num_3', '4', 
               'num_4', '5', 'num_5', 'escape']

    # Set images paths
    image_dir = op.join(data_dir, 'img_instructions')
    
    instr0_path = op.join(image_dir, 'instr1_pseudo.png')
    end_path = op.join(image_dir, 'end.png')
    instr2_path = op.join(image_dir, 'instr2_pseudo.png')
    instr3_path = op.join(image_dir, 'instr3_pseudo.png')
    valSAM_path = op.join(image_dir, 'valSAM.png')
    aroSAM_path = op.join(image_dir, 'aroSAM.png')

    slide_instr = visual.ImageStim(win, image=instr0_path, units="pix", 
                                   pos=(0, 0))
    slide_end = visual.ImageStim(win, image=end_path, units="pix", pos=(0, 0))
    instrValSAM = visual.ImageStim(win, image=instr2_path, units="pix", 
                                   pos=(0, 0))
    instrAroSAM = visual.ImageStim(win, image=instr3_path, units="pix", 
                                   pos=(0, 0))


    fixcross = visual.TextStim(win, text="+", units="norm", pos=(0, 0), 
                               color="black")
    valSAM = visual.ImageStim(win, image=valSAM_path, units="norm", pos=(0, 0))
    aroSAM = visual.ImageStim(win, image=aroSAM_path, units="norm", pos=(0, 0))

    ##### Show instructions #####
    show(slide_instr)
    wait_kbd_emo(kb)

    show(instrValSAM)
    wait_kbd_emo(kb)

    show(instrAroSAM)
    wait_kbd_emo(kb)
    
    ##### Start task #####
    names = []
    vals = []
    aros = []
    for n in range(len(audio_paths)):

        show(fixcross)
        core.wait(1.)
        send_trigger_thread(p, SN_TRIG)
        sd.play(sounds[n])
        sd.wait()
        names.append(audio_paths[n].split(os.sep)[-1]) 

        # Valence rating
        show(fixcross)
        core.wait(1.)
        slide_val = visual.TextStim(win, text=f"Valenza",font='Calibri', 
                                    units="norm", pos=(0, 0.6), color="black")
        slide_val.draw()
        valSAM.draw()
        win.flip()
        core.wait(.1)
        vals_resp = wait_kbd_emo(kb, okKeys=emoKeys)
        print(vals_resp.name)
        vals.append(vals_resp.name)


        # Arousal rating
        show(fixcross)
        slide_ar = visual.TextStim(win, text=f"Intensità Emotiva", 
                                   font='Calibri', units="norm", 
                                   pos=(0, 0.6), color="black")
        slide_ar.draw()
        aroSAM.draw()
        win.flip()
        core.wait(.1)
        aros_resp = wait_kbd_emo(kb, okKeys=emoKeys)
        print(aros_resp.name)    
        aros.append(aros_resp.name)


    show(slide_end)
    core.wait(2)
    win.close()
    save_emotion_scores(names, vals, aros, output_directory, 
                        subject_id, session)
    return


if __name__ == "__main__":
    task_B()

