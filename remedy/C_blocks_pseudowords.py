from remedy.utils.common_functions import check_os
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
from remedy.config.config import read_config
import random, glob, os
import os.path as op
import pandas as pd
import sounddevice as sd
import soundfile as sf
import parallel

from remedy.utils.common_functions import (wait_kbd_emo, get_meta, show, 
                                           send_trigger_thread)
from remedy.utils.find_devices import find_device
from psychopy import visual, core, monitors
from psychopy.hardware import keyboard


def create_blocks(category, cat_dir):
    file_cat = op.join(cat_dir, category)

    # Import items of each valence into separate lists
    items_pos = [file for file in glob.glob(op.join(file_cat, 'Pos*.jpg'))]
    items_neg = [file for file in glob.glob(op.join(file_cat, 'Neg*.jpg'))]
    items_neu = [file for file in glob.glob(op.join(file_cat, 'Neu*.jpg'))]

    # Shuffle the items list to get a random order
    random.shuffle(items_pos)
    random.shuffle(items_neg)
    random.shuffle(items_neu)

    # Ensure we have enough items to create 3 blocks of 11 images each
    min_length = max(len(items_pos), len(items_neg), len(items_neu))
    items_pos = items_pos[:min_length]
    items_neg = items_neg[:min_length]
    items_neu = items_neu[:min_length]

    items_all = [items_pos, items_neg, items_neu]

    # Split the items into a new lists with sequentially ordered valenced items (pos-neg-neu-pos-neg-neu....)
    items_mixed = [item for sublist in zip(*items_all) for item in sublist]

    # Ensure we have exactly 33 items
    assert len(items_mixed) == 33, AssertionError('Items number is not 33!')
    # items_mixed = items_mixed[:33]

    # Divide the items into 3 blocks of 11 images each
    items_block1 = items_mixed[:11]
    items_block2 = items_mixed[11:22]
    items_block3 = items_mixed[22:33]

    # Print the lengths of each block for debugging
    print(f"Block 1: {len(items_block1)} images")
    print(f"Block 2: {len(items_block2)} images")
    print(f"Block 3: {len(items_block3)} images")

    # Reshuffle the items list to get a random sequence
    random.shuffle(items_block1)
    random.shuffle(items_block2)
    random.shuffle(items_block3)

    return items_block1, items_block2, items_block3


def categ_current_block(block, dic_blocks):
    # This function takes a list of image names (block) as input and gives 
    # the corresponding category as an output.
    categ_map = {tuple(block): categ for categ in dic_blocks 
                 for block in dic_blocks[categ]}
    categ = categ_map.get(tuple(block), None)
    return categ


def task_C():
    
    # Define paths
    config = read_config()
    parent_dir = config['paths']['parent']
    data_dir = config['paths']['data']
    results_dir = config['paths']['results']
    
    outputname = get_meta()
    subject_id = outputname[0]
    session = int(outputname[1])
    
    output_directory = op.join(results_dir, f'RY{subject_id:03d}', 
                               f'N{session}', 'task_C')
    os.makedirs(output_directory, exist_ok=True)

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
    
    # Define audio device    
    devices = find_device()
    dev_hp = devices[0]
    sd.default.device = dev_hp
        
    # Define parallel port
    try:
        p = parallel.Parallel()
        print("Porta parallela aperta")
    except Exception as e:
        p = None
        print("Errore apertura porta parallela")
    
    # Define triggers
    SI_TRIG = 28 # Trigger for image and sound presentation

    # Set images paths
    cath_dir = op.join(data_dir, 'img_cathegories')
    image_dir = op.join(data_dir, 'img_instructions')

    instr1_path = os.path.join(image_dir, 'instr1_blocchi_pseudoparole.png')
    instr2_path = os.path.join(image_dir, 'instr_blocks_cycle.png')
    end_path = os.path.join(image_dir, 'end.png')

    slide_instr = visual.ImageStim(win, image=instr1_path, units="pix", 
                                   pos=(0, 0))
    slide_instr1 = visual.ImageStim(win, image=instr2_path, units="pix", 
                                   pos=(0, 0))
    slide_end = visual.ImageStim(win, image=end_path, units="pix", pos=(0, 0))

    # Fixation cross
    fixcross = visual.TextStim(win, text="+", units="norm", pos=(0, 0.2), 
                               color="black")

    # Set time variables (seconds)    
    image_duration = 2.5
    block_interval = 5

    all_combinations_path =  op.join(parent_dir, 'combinations', 
                                     'all_combinations_pseudo_day.csv')
    all_combinations_df = pd.read_csv(all_combinations_path)

    participant_combinations = all_combinations_df.loc[
        all_combinations_df['Participant_ID'] == subject_id]
    participant_current_categ = all_combinations_df[
            (all_combinations_df['Participant_ID'] == subject_id) & 
            (all_combinations_df['Session'] == session)]['Category'].tolist()
            
    blocks_current_sess = {cat: create_blocks(cat, cath_dir) 
                           for cat in participant_current_categ}

    # Create a list containing all the blocks as sublists, then shuffle it.
    # Stack together all the images of all the blocks considered 
    # for this session 
    all_blocks = [block for blocks in blocks_current_sess.values() 
                  for block in blocks]
    random.shuffle(all_blocks)

    # Create a list of all categories corresponding to the new shuffled 
    # order of blocks and make it a list
    all_categories = [categ_current_block(block, blocks_current_sess) 
                      for block in all_blocks]

    all_blocks_with_categories = list(zip(all_categories, all_blocks))

    # Create a list with the corresponding audio for each block
    all_blocks_audio_paths = [participant_combinations[
        participant_combinations['Category'] == cat]['Pseudo'].iloc[0] 
                              for cat in all_categories]
    sounds = [sf.read(audio)[0] for audio in all_blocks_audio_paths]
    
    log_imgnames = [[] for _ in range(len(all_blocks_with_categories))]
    log_imgcats = []
    log_imgaudios = []


    ##### Start task #####
    # Show instructions
    show(slide_instr)
    # core.wait(5)
    wait_kbd_emo(kb)
    
    # Present stimuli blocks three times
    # for cycle in range(2): # Testing only
    for cycle in range(3):

        for nblock in range(len(all_blocks_with_categories)):

            category, _ = all_blocks_with_categories[nblock]

            # Navigate in the folder of the block
            block_folder = op.join(cath_dir, category)
            slide_block = visual.TextStim(win, text=f"BLOCK {nblock + 1}",
                                          font="Calibri", units="norm", 
                                          pos=(0, 0.2), color="black")
            show(slide_block)
            core.wait(3)

            counter = 0
            for nimg in range(len(all_blocks[nblock])):

                imgname = all_blocks[nblock][nimg]
                show(fixcross)
                core.wait(1)
                win.flip()

                img_path = op.join(block_folder, imgname)
                send_trigger_thread(p, SI_TRIG)
                sd.play(sounds[nblock])
                img = visual.ImageStim(win, image=img_path, units="norm", 
                                       pos=(0, 0))
                show(img)
                core.wait(image_duration)
                
                if cycle == 0:
                    log_imgnames[nblock].append(imgname.split(os.sep)[-1])

                counter += 1

            if cycle == 0:
                log_imgcats.append(category)
                log_imgaudios.append(
                    all_blocks_audio_paths[nblock].split(os.sep)[-1])
            
            win.flip()
            show(fixcross)
            core.wait(block_interval)
                # if counter == 11: # TESTING PURPOSES ONLY - Limits block to X images
                #     break
        if cycle < 2:
            show(slide_instr1)
            wait_kbd_emo(kb)

    # --------------------------  EXPERIMENT END  -------------------------
    df = pd.DataFrame({
        'ImageName': log_imgnames,
        'Category': log_imgcats,
        'Audios': log_imgaudios,
    })

    df.to_csv(op.join(output_directory, f'RY{subject_id:03d}_N{session}.csv'),
                    index=False)
    show(slide_end)
    core.wait(2)
    win.close()

    return

if __name__ == "__main__":
    task_C()
