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
from psychopy import visual, core, event, monitors, sound
from psychopy.hardware import keyboard

def save_emotion_scores(names, vals, aros, disting, famil, rips, output_directory, subject_id, session):
    df = pd.DataFrame({
        'Audio': names,
        'Valence': vals,
        'Arousal': aros,
        'distinguibility': disting,
        'familiarity': famil,
        'ripetition': rips

    })
    df.to_csv(op.join(output_directory, f"AUDIO_EMO_SCORING_Pp{subject_id}_s_{session}.csv"), index=False)

def main():
    config = read_config()
    parent_dir = config['paths']['parent']
    audio_combinations = op.join(parent_dir, 'combinations', 'audio_commands.csv')
    audio_df = pd.read_csv(audio_combinations, sep=';')

    outputname = get_meta()
    subject_id = outputname[0]
    session = int(outputname[1])

    data_dir = config['paths']['data']
    base_audio_path = op.join(data_dir, 'audio_files')
    audio_paths = [op.join(base_audio_path, f'Audio_{i}.wav') for i in range(1, 7)]

    output_directory = op.join(parent_dir, 'data', 'output_wake')
    os.makedirs(output_directory, exist_ok=True)

    sounds = [sound.Sound(audio) for audio in audio_paths]

    names = []
    vals = []
    aros = []
    disting = []
    famil = []
    audios = []
    rips = ['0']

    widthPix = 1920  # screen width in px
    heightPix = 1080  # screen height in px
    monitorwidth = 54.3  # monitor width in cm
    viewdist = 60.  # viewing distance in cm
    monitorname = 'CH7210'
    #monitorname = 'DP-6'
    scrn = 1  # 0 to use main screen, 1 to use external screen
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
    instr0_path = op.join(image_dir, 'instr0_audio.png')
    end_path = op.join(image_dir, 'end.png')
    instr2_path = op.join(image_dir, 'instr2.png')
    instr3_path = op.join(image_dir, 'instr3.png')
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


    show(slideBrk_1)
    core.wait(5)

    #prima serie
    for index, snd in enumerate(sounds):
        slide_audio = visual.TextStim(win, text=f"Traccia {index + 1}", font='Calibri', units="norm", pos=(0, 0), color="black")
        show(slide_audio)
        snd.play()
        #core.wait(snd.getDuration())
        core.wait(5)
        snd.stop()
        show(fixcross)
        core.wait(1)

    #seconda serie
    show(slideBrk_2)
    core.wait(5)

    #seconda serie
    for nAudio, snd in enumerate(sounds):
        show(fixcross)
        core.wait(1)
        slide_audio = visual.TextStim(win, text=f"Traccia {nAudio + 1}", font='Calibri', units="norm", pos=(0, 0), color="black")
        show(slide_audio)
        snd.play()
        #core.wait(snd.getDuration())
        core.wait(5)
        snd.stop()

        dist.draw()
        win.flip()
        disting.append(wait_kbd_emo(kb, okKeys=emoKeys))

        fam.draw()
        win.flip()
        famil.append(wait_kbd_emo(kb, okKeys=emoKeys))


        if nAudio > 0:
            rip.draw()
            win.flip()
            rips.append(wait_kbd_emo(kb, okKeys=emoKeys))

        slide_val = visual.TextStim(win, text=f"Valenza",font='Calibri', units="norm", pos=(0, 0.6), color="black")
        slide_val.draw()
        valSAM.draw()
        win.flip()
        vals.append(wait_kbd_emo(kb, okKeys=emoKeys))

        slide_ar = visual.TextStim(win, text=f"Intensità Emotiva", font='Arial', units="norm", pos=(0, 0.6), color="black")
        slide_ar.draw()
        aroSAM.draw()
        win.flip()
        aros.append(wait_kbd_emo(kb, okKeys=emoKeys))
        names.append(audio_paths[nAudio])

        print(names)
        print(disting)
        print(aros)
        print(famil)
        print(rips)
        print(vals)

    show(slide_end)
    core.wait(2)
    win.close()
    if not (len(names) == len(vals) == len(aros) == len(disting) == len(famil) == len(rips)):
        print("Errore: le liste non hanno la stessa lunghezza.")
    else:
        save_emotion_scores(names, vals, aros, disting, famil, rips, output_directory, subject_id, session)


    # --------------------------  EXPERIMENT END  --------------------------

if __name__ == "__main__":
    main()


