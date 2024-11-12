from utils.common_functions import check_os
if check_os() in ['Linux']: 
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
from psychopy import visual, core, monitors
from psychopy.hardware import keyboard

import random, glob, os
import os.path as op
import pandas as pd
import parallel

from config.config import read_config
from utils.common_functions import (send_trigger_thread, wait_kbd_emo, 
                                           get_meta, show)


def save_emotion_scores(names, vals, aros, subject_id, session, res_dir):
    # output_directory = op.join(parent_dir, 'data', 'output_wake')
    # os.makedirs(output_directory, exist_ok=True)

    print("Length of names:", len(names))
    print("Length of vals:", len(vals))
    print("Length of aros:", len(aros))

    df = pd.DataFrame({
        'ImageName': names,
        'Valence': vals,
        'Arousal': aros
    })

    df.to_csv(op.join(res_dir, f'RY{subject_id:03d}_N{session}.csv'), 
              index=False)
    return


def task_A():
    config = read_config()
    parent_dir = config['paths']['parent']
    data_dir = config['paths']['data']
    results_dir = config['paths']['results']
    img_dir = op.join(data_dir, 'img_cathegories')

    all_combinations_path =  op.join(parent_dir, 'combinations', 
                                    'all_combinations_pseudo_day.csv')
    all_combinations_df = pd.read_csv(all_combinations_path)

    imgList = []
    outputname = get_meta()
    subject_id = outputname[0]
    session = int(outputname[1])
    
    res_dir_task_A = op.join(results_dir, f'RY{subject_id:03d}', f'N{session}', 'task_A')
    os.makedirs(res_dir_task_A, exist_ok=True)

    participant_current_combinations = all_combinations_df[
        (all_combinations_df['Participant_ID'] == subject_id) &
        (all_combinations_df['Session'] == session)]

    participant_current_categories = (
        participant_current_combinations['Category'].tolist())

    for category in participant_current_categories:
        category_images = glob.glob(op.join(img_dir, f'{category}/*.jpg'))
        imgList.extend(category_images)

    random.shuffle(imgList)
    # If you want to test a restricted number of images
    # imgList = imgList[:9]

    ##### PSYCHOPY SETTINGS #####
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

    # Check keyboard device according with the operative system
    if check_os() in ['Linux']:
        kb = keyboard.Keyboard(device=-1)
    elif check_os() in ['Windows', 'macOS']:
        kb = None
        
    emoKeys = ['1','num_1','2','num_2','3','num_3',
               '4','num_4','5','num_5','escape']

    ##### INSTRUCTIONS #####
    image_dir = op.join(data_dir, 'img_instructions')

    # Images paths
    instr1_path = os.path.join(image_dir, 'instr1.png')
    end_path = os.path.join(image_dir, 'end.png')
    instr2_path = os.path.join(image_dir, 'instr2.png')
    instr3_path = os.path.join(image_dir, 'instr3.png')
    valSAM_path = os.path.join(image_dir, 'valSAM.png')
    aroSAM_path = os.path.join(image_dir, 'aroSAM.png')
    slideBrk_path = os.path.join(image_dir, 'break.png')
    # Set slides
    slide_instr = visual.ImageStim(win, image=instr1_path, units="pix", 
                                   pos=(0, 0))
    slideBrk = visual.ImageStim(win, image=slideBrk_path, units="pix", 
                                pos=(0, 0))
    slide_end = visual.ImageStim(win, image=end_path, units="pix", pos=(0, 0))
    instrValSAM = visual.ImageStim(win, image=instr2_path, units="pix", 
                                   pos=(0, 0))
    instrAroSAM = visual.ImageStim(win, image=instr3_path, units="pix", 
                                   pos=(0, 0))
    # Fixation cross
    fixcross = visual.TextStim(win, text="+", units="norm", pos=(0, 0.2), 
                               color="black")
    fixcross.setAutoDraw(False)
    
    valSAM = visual.ImageStim(win, image=valSAM_path, units="norm", 
                              pos=(0, -0.8))
    aroSAM = visual.ImageStim(win, image=aroSAM_path, units="norm", 
                              pos=(0, -0.8))

    names = [0] * len(imgList)
    vals = [0] * len(imgList)
    aros = [0] * len(imgList)

    ##### SHOW INSTRUCTIONS #####
    show(slide_instr)
    wait_kbd_emo(kb)

    show(instrValSAM)
    wait_kbd_emo(kb)

    show(instrAroSAM)
    wait_kbd_emo(kb)
    
    # Inizializzazione della porta parallela LPT1
    try:
        p = parallel.Parallel()
        print("Porta parallela aperta")
    except Exception as e:
        p = None
        print("Errore apertura porta parallela")
    # Define trigger
    IG_TRIG = 24 # Trigger for image presentation
    
    # Start stimuli presentation
    counter = 0
    for n in range(len(imgList)):

        core.wait(.1)
        show(fixcross)
        core.wait(1.)
        win.flip()
        send_trigger_thread(p, IG_TRIG)
        img = visual.ImageStim(win, image=imgList[n], units="norm", 
                               pos=(0, 0.2))

        # idx = imgList[n].find('dxcat')
        # names[n] = imgList[n][idx + 6:-4]
        names[n] = imgList[n].split(os.sep)[-1]

        # Valence rating
        img.draw()
        valSAM.draw()
        win.flip()
        core.wait(.1)
        val_key = wait_kbd_emo(kb, okKeys=emoKeys)
        vals[n] = val_key.name
        core.wait(.1)

        # Arousal rating
        img.draw()
        aroSAM.draw()
        win.flip()
        core.wait(.1)
        aro_key = wait_kbd_emo(kb, okKeys=emoKeys)
        aros[n] = aro_key.name
        core.wait(.1)
        
        counter += 1

        if counter % 33 == 0 and counter != 99:
            show(slideBrk)
            core.wait(.1)
            wait_kbd_emo(kb)

    show(slide_end)
    core.wait(2.)
    win.close()
    save_emotion_scores(names, vals, aros, subject_id, session, res_dir_task_A)
    return


if __name__ == "__main__":
    ##### RUN TASK A #####
    task_A()
