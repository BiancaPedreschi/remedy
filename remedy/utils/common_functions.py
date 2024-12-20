from psychopy import core, event, gui
import platform
import time
import threading


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
    dlg.addField("Gender", choices=['Male', 'Female'])

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


def get_meta_test_od():
    dlg = gui.Dlg(title='Test per selezione')
    dlg.addField("Participant ID:")
    dlg.addField("Nome odore 1:", choices=['Limonene', 'Eugenolo', '2Phenylethanol', 'Heptanone', 'B-ionone',
                                           'A-terpineol','Geraniolo', 'Vanillina', 'Isoamyl Acetate'])
    dlg.addField("Nome odore 2", choices=['Limonene', 'Eugenolo', '2Phenylethanol', 'Heptanone', 'B-ionone',
                                          'A-terpineol','Geraniolo', 'Vanillina', 'Isoamyl Acetate'])

    params = dlg.show()

    if not dlg.OK:
        print("Action cancelled by user.")
        core.quit()

    snr, odor1, odor2 = params

    try:
        participant_id = int(snr)
    except ValueError:
        print("Participant ID is not a number, cancelling test.")
        core.quit()

    return participant_id, odor1, odor2


def wait_kbd(okkeys=["space", "escape"]):
    # mykey = event.waitKeys(keyList=okkeys)
    mykey = event.getKeys(keyList=okkeys)
    if mykey == ["space"]:
        return
    elif mykey == ["escape"]:
        core.quit()
    else:
        return mykey


def wait_kbd_emo(kb, okKeys=["space", "escape"], maxWait=float('inf')):
    if check_os() in ['Linux']:
        myKey = kb.waitKeys(maxWait=maxWait, keyList=okKeys, waitRelease=False,
                            clear=True)
        
        if myKey is not None:
            myKey = myKey[0]
            
        if myKey == "space":
            return myKey
        elif myKey == "escape":
            core.quit()
        else:
            return myKey
    elif check_os() in ['Windows', 'macOS']:
        myKey = event.waitKeys(maxWait=maxWait, keyList=okKeys)[0]
        if myKey == ["space"]:
            return
        elif myKey == ["escape"]:
            core.quit()
        else:
            return myKey

def wait_kbd_emo_and_get_time(kb, okKeys=["space", "escape", "right"]):
    if check_os() in ['Linux']:
        myKeys = kb.waitKeys(keyList=okKeys, waitRelease=False, clear=True)
        if myKeys:
            keyName = myKeys[0].name
            print(f"Key pressed: {keyName}")
            return keyName
    elif check_os() in ['Windows', 'macOS']:
        myKeys = event.waitKeys(keyList=okKeys)
        if myKeys:
            keyName = myKeys[0]
            print(f"Key pressed: {keyName}")
            return keyName
    return None


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

def str2num_2(resp):
    # Mappa sia i tasti numerici diretti che quelli del tastierino numerico ai loro valori numerici
    keydict = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
               'num_1': 1, 'num_2': 2, 'num_3': 3, 'num_4': 4, 'num_5': 5}
    try:
        # Assicurati che resp sia una lista e che il primo elemento abbia un attributo 'name'
        if isinstance(resp, list) and hasattr(resp[0], 'name'):
            keyName = resp[0].name
        else:
            keyName = resp  # Se resp non è una lista o non ha un attributo 'name', usa direttamente resp
        return int(keydict[keyName])
    except KeyError:
        print(f"Response '{resp}' is not a valid number key, cancelling test.")
        core.quit()
    except Exception as e:
        print(f"Unexpected error: {e}, cancelling test.")
        core.quit()
        

def show(stim: object) -> object:
    stim.draw()
    stim.win.flip()  # needed for two window setup - vs win.flip()


def send_trigger_thread(p, code, numlns=8):
    """
    Sends a trigger code converted to binary via serial port in a separate 
    thread.

    Args:
        p : porta parallela
        code (int): The numeric code to send.
        numlns (int, optional): The number of lines (or pins) to use for the 
            binary representation of the code. Default is 8.

    Returns:
        None
    """
    def trigger():
        print(f"Trigger inviato: {code}, binario: {code}")
        p.setData(code)
        time.sleep(0.005)
        p.setData(0)
    
    threading.Thread(target=trigger).start()
    return
