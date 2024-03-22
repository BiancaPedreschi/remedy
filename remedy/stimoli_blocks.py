from utils.common_functions import check_os
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
from config.config import read_config
import random, glob, os
import os.path as op
import pandas as pd
import time
from olfactometer_controller import olfactometer
from utils.common_functions import wait_kbd_emo, get_meta, show
from utils.find_serial import find_serial_device
from psychopy import visual, core, event, monitors
from psychopy.hardware import keyboard


config = read_config()
parent_dir = config['paths']['parent']

outputname = get_meta()
subject_id = outputname[0]
session = int(outputname[1])
data_dir = config['paths']['data']
mydir = op.join(data_dir, 'img_cathegories')

# _______________ OLFACTOMETER FUNCTIONS recalls
# port = "/dev/cu.usbmodem20220051"
# port = "/dev/ttyACM0"
###############################################################################
# TODO: test this:
# device_signature = 'f331:0002'
# port = find_serial_device(device_signature)
###############################################################################

# Defining olfactometer output dirs
output_directory = op.join(parent_dir, 'data', 'output_wake')
os.makedirs(output_directory, exist_ok=True)
current_day = time.strftime('%d%m%Y')
output_filename = f'stream_blocks_Pp{subject_id}_sess{session}_{current_day}.txt'
output_file_path = os.path.join(output_directory, output_filename)

###############################################################################
# olfm = olfactometer(output_file_path)
# olfm.set_serial(port=port)
# olfm.open()
###############################################################################

def create_blocks(category, cat_dir):
    """Given cathegories this function creates three blocks containing eleven 
    items balanced according with valence

    Args:
        category (str): _description_
        cat_dir (path_like): _description_

    Returns:
        _type_: _description_
    """

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


def get_odor_mapping(odors, categories):
    return [odors[cat] for cat in categories]


def handle_online_olf_shutdown(olfm, check_only=False):
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
            olfm.write('S 0')
            core.wait(3)
            print("interruzione manuale eseguita")
        except Exception as e:
            print(f"Errore durante la chiusura dell'olfattometro: {e}")
        finally:
            return True


    # ________________________ Create blocks for the current session's category
###############################################################################
# def main(olfm):
###############################################################################
def main():
    
    # Define paths
    config = read_config()
    parent_dir = config['paths']['parent']
    data_dir = config['paths']['data']
    #________________-   MONITOR   -

    # widthPix = 1920  # screen width in px
    # heightPix = 1080  # screen height in px
    widthPix = 800  # screen width in px
    heightPix = 600  # screen height in px
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

    kb = keyboard.Keyboard(device=-1)

    #________________ -  INSTRUCTIONS   -

    cath_dir = op.join(data_dir, 'img_cathegories')
    image_dir = op.join(data_dir, 'img_instructions')

    # Percorsi completi per le immagini
    instr1_path = os.path.join(image_dir, 'instr1_blocchi.png')
    end_path = os.path.join(image_dir, 'end.png')

    slide_instr = visual.ImageStim(win, image=instr1_path, units="pix", pos=(0, 0))
    slide_end = visual.ImageStim(win, image=end_path, units="pix", pos=(0, 0))

    # Fixation cross
    fixcross = visual.TextStim(win, text="+", units="norm", pos=(0, 0.2), color="black")

    ##---------- time variables in seconds

    # image_duration = 1.5
    # block_interval = 10.0
    
    image_duration = .2
    block_interval = .5

###############################################################################
    # #Configurazione iniziale dell'olfattometro
    # olfm.run()
    # olfm.write('C M;;;;;;;')
    # core.wait(0.5)
    # olfm.write('E 1')
    # core.wait(0.5)
    # olfm.write('S 0')
###############################################################################

    all_combinations_path =  op.join(parent_dir, 'combinations', 
                                     'all_combinations.csv')
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

    # Create a list with the corresponding odor for each block
    all_blocks_odor = [participant_combinations[participant_combinations['Category'] == cat]['Odor'].iloc[0] for cat in
                       all_categories]

#_____________ dizionario corrispondenza odori-comandi

    manualcomm_path = op.join(parent_dir, 'combinations', 'manual_commands.csv')
    manualcomm_df = pd.read_csv(manualcomm_path, sep=';')
    participant_current_combinations = manualcomm_df[
        (manualcomm_df['Participant_ID'] == subject_id) & (manualcomm_df['Session'] == session)]

    odor_command_map = {}
    
    # Itera sul dataframe dei comandi manuali
    for index, row in participant_current_combinations.iterrows():
        odor = row['Odor']
        command = row['Command']
        odor_command_map[odor] = command

    # Inizializza una lista vuota per i comandi degli odori
    all_block_commands = []

    # Itera su ogni odore nella lista all_block_odor
    for odor in all_blocks_odor:
        # Ottieni il comando corrispondente per l'odore dal dizionario odor_command_map
        command = odor_command_map.get(odor)
        # Aggiungi il comando alla lista dei comandi degli odori
        all_block_commands.append(command)
        
    #_______________________________
    # Utilizza le liste inizializzate esternamente
    log_imgnames = [[] for _ in range(len(all_blocks_with_categories))]
    log_imgcats = [[] for _ in range(len(all_blocks_with_categories))]
    log_imgodors = [[] for _ in range(len(all_blocks_with_categories))]
    log_imgcommands = [[] for _ in range(len(all_blocks_with_categories))]

##--------------------------  EXPERIMENT START  --------------------------
### --------------- Show instructions
    show(slide_instr)
    core.wait(5)
    wait_kbd_emo(kb)
## --------------- Present stimuli blocks twice
    for cycle in range(2):

###############################################################################
        # # Controlla se l'utente ha premuto 'q' a ogni iterazione
        # if handle_online_olf_shutdown(olfm,
        #                               check_only=False):
        #     break
###############################################################################

        for nblock in range(len(all_blocks_with_categories)):

            category, _ = all_blocks_with_categories[nblock]

            # Navigate in the folder of the block
            block_folder = op.join(cath_dir, category)
            slide_block = visual.TextStim(win, text=f"BLOCK {nblock + 1}", units="norm", pos=(0, 0.2), color="black")
            show(slide_block)
###############################################################################
            # olfm.write('S 0')
###############################################################################
            core.wait(block_interval)

            counter = 0

            for nimg in range(len(all_blocks[nblock])):

                imgname = all_blocks[nblock][nimg]
                show(fixcross)
                core.wait(0.1)

                img_path = op.join(block_folder, imgname)

###############################################################################
                # olfm.write(all_block_commands[nblock])
###############################################################################
                img = visual.ImageStim(win, image=img_path, units="norm", pos=(0, 0))
                show(img)
                core.wait(image_duration)
                
                if cycle == 0:
                    log_imgnames[nblock].append(imgname)
                    log_imgcats[nblock].append(category)
                    log_imgodors[nblock].append(all_blocks_odor[nblock])
                    log_imgcommands[nblock].append(all_block_commands[nblock])

                counter += 1

                if counter > 2: # TESTING PURPOSES ONLY - Limits block to X images
###############################################################################
                    # olfm.write('S 0')
                    # core.wait(0.5)
###############################################################################
                    break
            
###############################################################################
    # olfm.write('S 0')
    # show(slide_end)
    # core.wait(5)
    # show(fixcross)
    # core.wait(2)
    # win.close()

    # olfm.write('E 0')
    # core.wait(0.5)
    # olfm.stop()
    # core.wait(0.5)
    # olfm.close()
###############################################################################

        # --------------------------  EXPERIMENT END  --------------------------
    df = pd.DataFrame({
        'ImageName': log_imgnames,
        'Category': log_imgcats,
        'Odor': log_imgodors,
        'Participant': [subject_id] * len(log_imgnames),
        'Session': [session] * len(log_imgnames),
        'Commands': log_imgcommands
    })


    df.to_csv(op.join(output_directory, 
                      f"BLOCKS_Pp{subject_id}_session_{session}.csv"), 
              index=False)


if __name__ == "__main__":
    # main(olfm)
    main()
