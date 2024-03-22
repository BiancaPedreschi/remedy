from psychopy import core, event, gui
import platform


def check_os():
    plf = platform.platform().split('-')[0]
    return plf

##_____finestra input info part_id e sess + lista con info
def get_meta():
    dlg = gui.Dlg(title='REMEDY-Wake Task')
    dlg.addField("Participant ID:")
    dlg.addField("Session:", choices=['1', '2'])

    params = dlg.show()

    if not dlg.OK:
        print("Action cancelled by user.")
        core.quit()

    snr, session = params

    try:
        participant_id = int(snr)
    except ValueError:
        print("Participant ID is not a number, cancelling test.")
        core.quit()

    # lst.extend([participant_id, session])


    # output_name = os.path.join(folder_path, file_name)
    return participant_id, session


def get_meta_night():
    dlg = gui.Dlg(title='REMEDY-Wake Task')
    dlg.addField("Participant ID:")
    dlg.addField("Session:", choices=['1', '2'])
    dlg.addField("Gender", choices=['M', 'F'])

    params = dlg.show()

    if not dlg.OK:
        print("Action cancelled by user.")
        core.quit()

    snr, session, gnd = params

    try:
        participant_id = int(snr)
    except ValueError:
        print("Participant ID is not a number, cancelling test.")
        core.quit()
        
    return participant_id, session, gnd


def wait_kbd(okkeys=["space", "escape"]):
    # mykey = event.waitKeys(keyList=okkeys)
    mykey = event.getKeys(keyList=okkeys)
    if mykey == ["space"]:
        return
    elif mykey == ["escape"]:
        core.quit()
    else:
        return mykey


def wait_kbd_emo(kb, okKeys=["space", "escape"]):
    if check_os() in ['Linux']:
        myKey = kb.waitKeys(keyList=okKeys, waitRelease=False, clear=True)
        if myKey == "space":
            return
        elif myKey == "escape":
            core.quit()
        else:
            return myKey
    elif check_os() in ['Windows', 'macOS']:
        mykey = event.waitKeys(keyList=okKeys)
        if mykey == ["space"]:
            return
        elif mykey == ["escape"]:
            core.quit()
        else:
            return mykey


# Pause until a specified key is hit and save the hit key
def get_kbd(okkeys=None):
    pressedkeys = []
    while True:
        mykey = event.waitKeys(keyList=okkeys)
        print(mykey)
        if mykey == ["space"]:
            return pressedkeys
        elif mykey == ["escape"]:
            core.quit()
        else:
            pressedkeys.extend(mykey)
            print(pressedkeys)
        
        
def str2num(resp):
    keydict = {'num_1': 1, 'num_2': 2, 'num_3': 3, 'num_4': 4, 'num_5': 5}
    try:
        return int(keydict[resp[0].name])
    except Exception:
        print("Response is not a number, cancelling test.")
        core.quit()
        

def show(stim):
    stim.draw()
    stim.win.flip()  # needed for two window setup - vs win.flip()
