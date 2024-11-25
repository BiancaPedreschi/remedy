import sounddevice as sd
import soundfile as sf
from remedy.config.config import read_config
import os
import os.path as op
from remedy.utils.common_functions import (wait_kbd_emo, show, check_os)
from remedy.utils.find_devices import find_device
from psychopy import visual, core, monitors, sound
from psychopy.hardware import keyboard

def adjust_volume(orig_PP, new_PP, volume_PP=1, fs=24000):
    for opn, npn in zip(orig_PP, new_PP):
        print(f"Processing file: {opn}") 
        _opn, _file_fs = sf.read(opn)
        if _file_fs != fs:
            print(f"Warning: Sample rate mismatch. File sample rate is {_file_fs}, expected {fs}")
        _npn = _opn * volume_PP
        sd.play(_npn, samplerate=_file_fs)
        sd.wait()
        # core.wait(1)
        sf.write(npn, _npn, _file_fs)

def test_volume_threshold(orig_PP, new_PP, initial_volume=0.05, decrement=0.005, test_count=20):
    volume_PP = initial_volume
    lower_decrement = 0.001
    while volume_PP > 0:
        if volume_PP <= 0.01:
            decrement = lower_decrement
        instruction_text.text = "Premi 'SPACE' per continuare, 'R' se il minimo è stato raggiunto, 'Q' per terminare."
        instruction_text.draw()
        win.flip()


        response = wait_kbd_emo(kb, okKeys=emoKeys, maxWait=18)
        if response == 'q':
            break
        elif response == 'space':
            show(fixcross_w)
            core.wait(.25)
            win.flip()
            core.wait(.25)
            show(fixcross_w)
            adjust_volume(orig_PP, new_PP, volume_PP=volume_PP)
            print('volume corrente:', volume_PP)
        
        elif response == 'r':
            volume_PP += decrement
            print('volume raggiunto:', volume_PP)
            # Se il soggetto non sente più, torna indietro di un punto
            for _ in range(test_count):
                adjust_volume(B_orig_fname_PP, B_new_fname_PP, volume_PP=volume_PP)
                print('volume corrente:', volume_PP)
                instruction_text.text = "Se non riuscivi a distinguere le pseudoparole, premi 'M' per tornare indietro di un punto."
                instruction_text.draw()
                win.flip()
                # Verifica se il soggetto distingue le pseudoparole
                response = wait_kbd_emo(kb, okKeys=emoKeys, maxWait=18)
                if response == 'm':
                    volume_PP += lower_decrement
                    print('volume raggiunto:', volume_PP)
                    adjust_volume(B_orig_fname_PP, B_new_fname_PP, volume_PP=volume_PP)
                    instruction_text.text = "Se non riuscivi a distinguere le pseudoparole, premi 'M' per tornare indietro di un punto."
                    instruction_text.draw()
                    win.flip()
                    response = wait_kbd_emo(kb, okKeys=emoKeys, maxWait=18)
                    if response == 'm':
                        volume_PP += lower_decrement
                        print('volume raggiunto:', volume_PP)
                        adjust_volume(B_orig_fname_PP, B_new_fname_PP, volume_PP=volume_PP)
                        instruction_text.text = "Se non riuscivi a distinguere le pseudoparole, premi 'M' per tornare indietro di un punto."
                        instruction_text.draw()
                        win.flip()
                        response = wait_kbd_emo(kb, okKeys=emoKeys, maxWait=18)
                        if response == 'm':
                            volume_PP += lower_decrement
                            print('volume raggiunto:', volume_PP)
                            adjust_volume(B_orig_fname_PP, B_new_fname_PP, volume_PP=volume_PP)
                            instruction_text.text = "Se non riuscivi a distinguere le pseudoparole, premi 'M' per tornare indietro di un punto."
                            instruction_text.draw()
                            win.flip()
                            response = wait_kbd_emo(kb, okKeys=emoKeys, maxWait=18)
                            if response == 'm':
                                volume_PP += lower_decrement    
                                print('volume raggiunto:', volume_PP)
                                adjust_volume(B_orig_fname_PP, B_new_fname_PP, volume_PP=volume_PP)
                                instruction_text.text = "Se non riuscivi a distinguere le pseudoparole, premi 'M' per tornare indietro di un punto."
                                instruction_text.draw()
                                win.flip()
                        break
                    break
            break
        
        volume_PP -= decrement
        
# Esegui il test del volume

# Define paths and stimuli
config = read_config()
data_dir = config['paths']['data']
PP_letters = ['a', 'b', 'c']

A_orig_fname_PP = [op.join(data_dir, 'pwd_treshold_originals', f'pseudoparola_a.wav')]
A_new_fname_PP = [op.join(data_dir, 'pwd_treshold', f'pseudoparola_a.wav')]
B_orig_fname_PP = [op.join(data_dir, 'pwd_treshold_originals', f'pseudoparola_{fn}.wav') for fn in PP_letters]
B_new_fname_PP = [op.join(data_dir, 'pwd_treshold', f'pseudoparola_{fn}.wav') for fn in PP_letters]

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
fixcross = visual.TextStim(win, text="+", units="norm", 
                            pos=(0, 0), color="black")
fixcross_w = visual.TextStim(win, text="+", units="norm", 
                            pos=(0, 0), color="white")
instruction_text = visual.TextStim(win, text='', pos=(0, 0), height=0.05, font='Arial' , bold=True)

if check_os() in ['Linux', 'macOS']:
    kb = keyboard.Keyboard(device=-1)
elif check_os() in ['Windows']:
    # kb = None
    kb = keyboard.Keyboard()

emoKeys = ['space', 'r', 'q', 'm']


show(fixcross)
core.wait(2)
test_volume_threshold(A_orig_fname_PP, A_new_fname_PP, initial_volume=0.05, decrement=0.005, test_count=10)
