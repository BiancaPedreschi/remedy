from utils.common_functions import check_os
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
from config.config import read_config
import random, glob, os
import os.path as op
import pandas as pd

from utils.common_functions import wait_kbd_emo, get_meta, show
from psychopy import visual, core, event, monitors, sound
from psychopy.hardware import keyboard


config = read_config()
parent_dir = config['paths']['parent']

outputname = get_meta()
subject_id = outputname[0]
session = int(outputname[1])
data_dir = config['paths']['data']
mydir = op.join(data_dir, 'img_cathegories')

def create_blocks(category, cat_dir):
    file_cat = os.path.join(cat_dir, category)

    os.chdir(file_cat)

    # Import items of each valence into separate lists
    items_pos = [file for file in glob.glob('Pos*.jpg')]
    items_neg = [file for file in glob.glob('Neg*.jpg')]
    items_neu = [file for file in glob.glob('Neu*.jpg')]

    # Shuffle the items list to get a random order
    random.shuffle(items_pos)
    random.shuffle(items_neg)
    random.shuffle(items_neu)

    items_all = [items_pos, items_neg, items_neu]

    # Split the items into a new lists with sequentially ordered valenced items (pos-neg-neu-pos-neg-neu....)
    items_mixed = [item for sublist in zip(*items_all) for item in sublist]

    items_block1 = items_mixed[:11]
    items_block2 = items_mixed[11:22]
    items_block3 = items_mixed[22:]

    # Reshuffle the items list to get a random sequence
    random.shuffle(items_block1)
    random.shuffle(items_block2)
    random.shuffle(items_block3)
    return items_block1, items_block2, items_block3


def categ_current_block(block, dic_blocks):
    # This function takes a list of image names (block) as input and gives the corresponding category as an output.
    categ_map = {tuple(block): categ for categ in dic_blocks for block in dic_blocks[categ]}
    categ = categ_map.get(tuple(block), None)
    return categ


def main():
    
    # Define paths
    config = read_config()
    parent_dir = config['paths']['parent']
    data_dir = config['paths']['data']
    output_directory = op.join(parent_dir, 'data', 'output_wake')


    #________________-   MONITOR   -


    widthPix = 1920  # screen width in px
    heightPix = 1080  # screen height in px
    monitorwidth = 54.3  # monitor width in cm
    viewdist = 60.  # viewing distance in cm
    monitorname = 'CH7210'
    #monitorname = 'DP-6'
    scrn = 1  # 0 to use main screen, 1 to use external screen
    mon = monitors.Monitor(monitorname, width=monitorwidth, distance=viewdist)
    mon.setSizePix((widthPix, heightPix))

    win = visual.Window(fullscr=False, size=(widthPix, heightPix), color="grey", 
                        units='pix', monitor=mon, pos=(0, -0.2), screen=scrn,
                        winType="pyglet") 
    
    if check_os() in ['Linux']:
        kb = keyboard.Keyboard(device=-1)
    elif check_os() in ['Windows', 'macOS']:
        kb = None

    #________________ -  INSTRUCTIONS   -

    cath_dir = op.join(data_dir, 'img_cathegories')
    image_dir = op.join(data_dir, 'img_instructions')

    # Percorsi completi per le immagini
    instr1_path = os.path.join(image_dir, 'instr1_blocchi_sound.png')
    end_path = os.path.join(image_dir, 'end.png')

    slide_instr = visual.ImageStim(win, image=instr1_path, units="pix", pos=(0, 0))
    slide_end = visual.ImageStim(win, image=end_path, units="pix", pos=(0, 0))

    # Fixation cross
    fixcross = visual.TextStim(win, text="+", units="norm", pos=(0, 0.2), color="black")

    ##---------- time variables in seconds

    # image_duration = 1.5
    # block_interval = 10.0
    
    image_duration = 2
    block_interval = 5


    all_combinations_path =  op.join(parent_dir, 'combinations', 
                                     'all_combinations_audio_2secv1.csv')
    all_combinations_df = pd.read_csv(all_combinations_path)

    participant_combinations = all_combinations_df.loc[all_combinations_df['Participant_ID'] == subject_id]
    participant_current_categ = all_combinations_df[
            (all_combinations_df['Participant_ID'] == subject_id) & (all_combinations_df['Session'] == session)][
            'Category'].tolist()
            
    blocks_current_sess = {cat: create_blocks(cat, cath_dir) for cat in participant_current_categ}

    # Create a list containing all the blocks as sublists, then shuffle it.
    # Stack together all the images of all the blocks considered for this session 
    all_blocks = [block for blocks in blocks_current_sess.values() for block in blocks]
    random.shuffle(all_blocks)

    # Create a list of all categories corresponding to the new shuffled order of blocks and make it a list
    all_categories = [categ_current_block(block, blocks_current_sess) for block in all_blocks]

    all_blocks_with_categories = list(zip(all_categories, all_blocks))

    # Create a list with the corresponding audio for each block
    all_blocks_audio_paths = [participant_combinations[participant_combinations['Category'] == cat]['Audio'].iloc[0] for cat in
                       all_categories]
    sounds = [sound.Sound(audio) for audio in all_blocks_audio_paths]
        
    #_______________________________
    # Utilizza le liste inizializzate esternamente
    log_imgnames = [[] for _ in range(len(all_blocks_with_categories))]
    log_imgcats = [[] for _ in range(len(all_blocks_with_categories))]
    log_imgaudios = [[] for _ in range(len(all_blocks_with_categories))]
    log_imgcommands = [[] for _ in range(len(all_blocks_with_categories))]

##--------------------------  EXPERIMENT START  --------------------------
### --------------- Show instructions
    show(slide_instr)
    core.wait(5)
    wait_kbd_emo(kb)
## --------------- Present stimuli blocks twice
    for cycle in range(2):

        for nblock in range(len(all_blocks_with_categories)):

            category, _ = all_blocks_with_categories[nblock]

            # Navigate in the folder of the block
            block_folder = op.join(cath_dir, category)
            slide_block = visual.TextStim(win, text=f"BLOCK {nblock + 1}", font='Calibri', units="norm", pos=(0, 0.2), color="black")
            show(slide_block)
            core.wait(block_interval)

            counter = 0

            for nimg in range(len(all_blocks[nblock])):

                imgname = all_blocks[nblock][nimg]
                show(fixcross)
                core.wait(0.1)

                img_path = op.join(block_folder, imgname)
                sounds[nblock].play()
                img = visual.ImageStim(win, image=img_path, units="norm", pos=(0, 0))
                show(img)
                core.wait(image_duration)
                
                if cycle == 0:
                    log_imgnames[nblock].append(imgname)
                    log_imgcats[nblock].append(category)
                    log_imgaudios[nblock].append(all_blocks_audio_paths[nblock])
                    log_imgcommands[nblock].append(all_blocks_audio_paths[nblock])

                counter += 1

                if counter > 2: # TESTING PURPOSES ONLY - Limits block to X images
                    break


        # --------------------------  EXPERIMENT END  --------------------------
    df = pd.DataFrame({
        'ImageName': log_imgnames,
        'Category': log_imgcats,
        'Audios': log_imgaudios,
        'Participant': [subject_id] * len(log_imgnames),
        'Session': [session] * len(log_imgnames),
        'Commands': log_imgcommands
    })

    df.to_csv(op.join(output_directory, 
                      f"BLOCKS_Sounds_Pp{subject_id}_session_{session}.csv"),
              index=False)
    show(slide_end)
    core.wait(2)
    win.close()

if __name__ == "__main__":
    main()
