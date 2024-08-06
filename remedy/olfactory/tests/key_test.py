import ctypes
xlib = ctypes.cdll.LoadLibrary("libX11.so")
xlib.XInitThreads()
from psychopy.hardware import keyboard

kb = keyboard.Keyboard(device=-1)

while True:
    # keys = kb.getKeys(['space', '2'], waitRelease=False, clear=True)
    keys = kb.waitKeys(keyList=['space', '2'], waitRelease=False, clear=True)

    for k in keys:
        if k == 'space':
            print('Space!')
        elif k == '2':
            print('two!')