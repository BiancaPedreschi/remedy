from utils.common_functions import check_os
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
from config.config import read_config
import os
import os.path as op
import random
import pandas as pd
from utils.common_functions import wait_kbd_emo, get_meta, show, str2num
from psychopy import visual, core, event, monitors, sound
from psychopy.hardware import keyboard

def save_emotion_scores(names, vals, aros, output_directory, subject_id, session):
    df = pd.DataFrame({
        'Audio': names,
        'Valence': vals,
        'Arousal': aros,

    })
    df.to_csv(op.join(output_directory, f"emoscoring_PSEUDOWORDS_Pp{subject_id}_s_{session}.csv"), index=False)

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
    audio_paths = filtered_df['Pseudo'].tolist()
    print(audio_paths)

    output_directory = op.join(parent_dir, 'data', 'output_wake')
    os.makedirs(output_directory, exist_ok=True)

    sounds = [sound.Sound(audio) for audio in audio_paths]  

    names = []
    vals = []
    aros = []


    # widthPix = 1920  # screen width in px
    # heightPix = 1080  # screen height in px
    # monitorwidth = 54.3  # monitor width in cm
    # viewdist = 60.  # viewing distance in cm
    # monitorname = 'CH7210'
    # #monitorname = 'DP-6'
    # scrn = 1  # 0 to use main screen, 1 to use external screen
    widthPix = 2560  # screen width in px
    heightPix = 1440  # screen height in px
    monitorwidth = 28.04  # monitor width in cm (puoi mantenere questo valore se è corretto)
    viewdist = 60.  # viewing distance in cm (puoi mantenere questo valore se è corretto)
    monitorname = 'MacBook Pro 13"'
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
    emoKeys = ['1', 'num_1', '2', 'num_2', '3', 'num_3', '4', 'num_4', '5', 'num_5', 'escape']

    # ________________ -  INSTRUCTIONS   -
    image_dir = op.join(data_dir, 'img_instructions')

    # Percorsi completi per le immagini
    instr0_path = op.join(image_dir, 'instr1_pseudo.png')
    end_path = op.join(image_dir, 'end.png')
    instr2_path = op.join(image_dir, 'instr2_pseudo.png')
    instr3_path = op.join(image_dir, 'instr3_pseudo.png')
    valSAM_path = op.join(image_dir, 'valSAM.png')
    aroSAM_path = op.join(image_dir, 'aroSAM.png')
    slideBrk_path_1 = op.join(image_dir, 'prima_s.png')
    slideBrk_path_2 = op.join(image_dir, 'seconda_s.png')
    dist_path = op.join(image_dir, 'dist.png')
    fam_path = op.join(image_dir, 'fam.png')
    rip_path = op.join(image_dir, 'rip.png')

    slide_instr = visual.ImageStim(win, image=instr0_path, units="pix", pos=(0, 0))
    slideBrk_1 = visual.ImageStim(win, image=slideBrk_path_1, units="pix", pos=(0, 0))
    slideBrk_2 = visual.ImageStim(win, image=slideBrk_path_2, units="pix", pos=(0, 0))
    slide_end = visual.ImageStim(win, image=end_path, units="pix", pos=(0, 0))
    instrValSAM = visual.ImageStim(win, image=instr2_path, units="pix", pos=(0, 0))
    instrAroSAM = visual.ImageStim(win, image=instr3_path, units="pix", pos=(0, 0))


    fixcross = visual.TextStim(win, text="+", units="norm", pos=(0, 0), color="black")
    valSAM = visual.ImageStim(win, image=valSAM_path, units="norm", pos=(0, 0))
    aroSAM = visual.ImageStim(win, image=aroSAM_path, units="norm", pos=(0, 0))
    dist = visual.ImageStim(win, image=dist_path, units="norm", pos=(0, 0))
    fam = visual.ImageStim(win, image=fam_path, units="norm", pos=(0, 0))
    rip = visual.ImageStim(win, image=rip_path, units="norm", pos=(0, 0))


    # --------------------------  INSTRUCTIONS  --------------------------
    show(slide_instr)
    wait_kbd_emo(kb)

    show(instrValSAM)
    wait_kbd_emo(kb)

    show(instrAroSAM)
    wait_kbd_emo(kb)


    for n in range(len(audio_paths)):

        timer = core.Clock()  # TESTING PURPOSES ONLY - Image rating timing

        show(fixcross)
        core.wait(1.)
        sounds[n].play()
        core.wait(sounds[n].getDuration())
        sounds[n].stop()
        names.append(audio_paths[n]) 

        # Valence rating
        show(fixcross)
        core.wait(1.)
        slide_val = visual.TextStim(win, text=f"Valenza",font='Calibri', units="norm", pos=(0, 0.6), color="black")
        slide_val.draw()
        valSAM.draw()
        win.flip()
        vals_resp = wait_kbd_emo(kb, okKeys=emoKeys)
        print(vals_resp)
        vals.append(vals_resp)


        # Arousal rating
        show(fixcross)
        slide_ar = visual.TextStim(win, text=f"Intensità Emotiva", font='Calibri', units="norm", pos=(0, 0.6), color="black")
        slide_ar.draw()
        aroSAM.draw()
        win.flip()
        aros_resp = wait_kbd_emo(kb, okKeys=emoKeys)
        print(aros_resp)    
        aros.append(aros_resp)


    show(slide_end)
    core.wait(2)
    win.close()
    save_emotion_scores(names, vals, aros, output_directory, subject_id, session)

    # --------------------------  EXPERIMENT END  --------------------------

if __name__ == "__main__":
    main()

