from utils.common_functions import check_os
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
from config.config import read_config
import random, glob, os
import os.path as op
import pandas as pd
from utils.common_functions import wait_kbd_emo, get_meta, show, str2num
from psychopy import visual, core, event, monitors
from psychopy.hardware import keyboard


config = read_config()
parent_dir = config['paths']['parent']

all_combinations_path =  op.join(parent_dir, 'combinations', 
                                 'all_combinations.csv')
all_combinations_df = pd.read_csv(all_combinations_path)

imgList = []
outputname = get_meta()
subject_id = outputname[0]
session = int(outputname[1])

data_dir = config['paths']['data']
mydir = op.join(data_dir, 'img_cathegories')

participant_current_combinations = all_combinations_df[
    (all_combinations_df['Participant_ID'] == subject_id) &
    (all_combinations_df['Session'] == session)]

participant_current_categories = (
    participant_current_combinations['Category'].tolist())

for category in participant_current_categories:
    category_images = glob.glob(op.join(mydir, f'{category}/*.jpg'))
    imgList.extend(category_images)

random.shuffle(imgList)
imgList = imgList[:10]

#________________-   HARDWARE PARAMETER -

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

if check_os() in ['Linux']:
    kb = keyboard.Keyboard(device=-1)
elif check_os() in ['Windows', 'macOS']:
    kb = None
    
emoKeys = ['1','num_1','2','num_2','3','num_3','4','num_4','5','num_5','escape']

#________________ -  INSTRUCTIONS   -
# image_dir = '/Users/foscagiannotti/Desktop/project_remedy/img_istruzioni'
image_dir = op.join(data_dir, 'img_instructions')

# Percorsi completi per le immaginis
instr1_path = os.path.join(image_dir, 'instr1.png')
end_path = os.path.join(image_dir, 'end.png')
instr2_path = os.path.join(image_dir, 'instr2.png')
instr3_path = os.path.join(image_dir, 'instr3.png')
valSAM_path = os.path.join(image_dir, 'valSAM.png')
aroSAM_path = os.path.join(image_dir, 'aroSAM.png')
slideBrk_path = os.path.join(image_dir, 'break.png')


slide_instr = visual.ImageStim(win, image=instr1_path, units="pix", pos=(0, 0))
slideBrk = visual.ImageStim(win, image=slideBrk_path, units="pix", pos=(0, 0))
slide_end = visual.ImageStim(win, image=end_path, units="pix", pos=(0, 0))
instrValSAM = visual.ImageStim(win, image=instr2_path, units="pix", pos=(0, 0))
instrAroSAM = visual.ImageStim(win, image=instr3_path, units="pix", pos=(0, 0))

# Fixation cross
fixcross = visual.TextStim(win, text="+", units="norm", pos=(0, 0.2), 
                           color="black")
valSAM = visual.ImageStim(win, image=valSAM_path, units="norm", pos=(0, -0.8))
aroSAM = visual.ImageStim(win, image=aroSAM_path, units="norm", pos=(0, -0.8))

names = [0] * len(imgList)
vals = [0] * len(imgList)
aros = [0] * len(imgList)

# --------------------------  INSTRUCTIONS  --------------------------
show(slide_instr)
wait_kbd_emo(kb)

show(instrValSAM)
wait_kbd_emo(kb)

show(instrAroSAM)
wait_kbd_emo(kb)

# --------------------------  EXPERIMENT START  --------------------------
def save_emotion_scores(names, vals, aros):
    # output_directory = "/Users/foscagiannotti/Desktop/project_remedy/WT_output"
    output_directory = op.join(parent_dir, 'data', 'output_wake')
    os.makedirs(output_directory, exist_ok=True)
    # os.chdir(output_directory)

    print("Length of names:", len(names))
    print("Length of vals:", len(vals))
    print("Length of aros:", len(aros))


    df = pd.DataFrame({
        'ImageName': names,
        'Valence': vals,
        'Arousal': aros
    })

    df.to_csv(op.join(output_directory, 
                      f"IMG_EMO_SCORING_Pp{subject_id}_session_{session}.csv"), 
              index=False)

def main ():
    counter = 0

    for n in range(len(imgList)):

        timer = core.Clock()  # TESTING PURPOSES ONLY - Image rating timing

        show(fixcross)
        core.wait(1.)
        img = visual.ImageStim(win, image=imgList[n], units="norm", 
                               pos=(0, 0.2))

        idx = imgList[n].find('dxcat')
        names[n] = imgList[n][idx + 6:-4]

        # Valence rating
        img.draw()
        valSAM.draw()
        win.flip()
        vals[n] = str2num(wait_kbd_emo(kb, okKeys=emoKeys))

        # Arousal rating
        img.draw()
        aroSAM.draw()
        win.flip()
        aros[n] = str2num(wait_kbd_emo(kb, okKeys=emoKeys))

        #  timing of imag rating
        counter += 1

        if counter % 50 == 0:  # May be edited for testing purposes -> break every X images (change to %100 when exp)
            show(slideBrk)
            wait_kbd_emo(kb)

    show(slide_end)
    core.wait(2.)
    win.close()

    save_emotion_scores(names, vals, aros)

    # --------------------------  EXPERIMENT END  --------------------------

if __name__ == "__main__":
    main()
