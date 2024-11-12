import pyaudio
import wave
import pyaudio
import wave
import time

from psychopy import visual
# from psychopy import prefs
from psychopy.hardware import keyboard
from remedy.utils.common_functions import check_os

# prefs.hardware['audioLib'] = ['sounddevice', 'pyo', 'pygame', 'PTB']
# prefs.hardware['audioDevice'] = 'sysdefault'
# prefs.hardware['audioLatencyMode'] = 3

if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
    
if check_os() in ['Linux']:
    kb = keyboard.Keyboard(device=-1)
elif check_os() in ['Windows', 'macOS']:
    kb = keyboard.Keyboard() 

win = visual.Window(fullscr=False, color="black", units="norm")
instruction_text = visual.TextStim(win, text=' prova prova', pos=(0, 0), height=0.05)


instruction_text.draw()
win.flip()


def play_audio(file_path, device_index):
    wf = wave.open(file_path, 'rb')
    audio = pyaudio.PyAudio()

    def callback(in_data, frame_count, time_info, status):
        # print('Callback function called')
        data = wf.readframes(frame_count)
        if len(data) < frame_count * wf.getsampwidth():
            wf.rewind()
            data += wf.readframes(frame_count - len(data) // wf.getsampwidth())
            # data += wf.readframes(0)
            print(frame_count - len(data) // wf.getsampwidth())
            print(len(data))
            print(frame_count)
            print(wf.getsampwidth())
            print("\n")
        return (data, pyaudio.paContinue)

    stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        output_device_index=device_index,
                        stream_callback=callback)
    stream.start_stream()
    return stream, audio

# def play_audio(file_path, device_index):
#     wf = wave.open(file_path, 'rb')
#     audio = pyaudio.PyAudio()

#     stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
#                         channels=wf.getnchannels(),
#                         rate=wf.getframerate(),
#                         output=True,
#                         output_device_index=device_index,
#                         stream_callback=None)
#     stream.start_stream()
#     return stream, audio


def stop_audio(stream, audio):
    stream.stop_stream()
    stream.close()
    audio.terminate()

# Esempio di utilizzo
pink_noise_file = '/Users/foscagiannotti/Desktop/python_projects/space/remedy/data/pwd/PN_segments/M_PN_2.5s_11.wav'
pseudoparola_file = '/Users/foscagiannotti/Desktop/python_projects/space/remedy/data/pwd/night_stim/pseudoparola_A.wav'

dev_sp = 3
dev_hp = 3

# Riproduci il pink noise su dev_sp
# stream_pink, audio_pink = play_audio(pink_noise_file, device_index=dev_sp)
print("Pink noise avviato.")
# time.sleep(5)
stream_pseudo, audio_pseudo = play_audio(pseudoparola_file, device_index=dev_hp)
keys = kb.waitKeys(keyList=['n', 'w', 's', 'escape', 'esc'])
# Riproduci le pseudoparole su dev_hp
for i in range(10):
    stream_pseudo, audio_pseudo = play_audio(pseudoparola_file, device_index=dev_hp)
    print("Pseudoparole avviate.")
    # while stream_pseudo.is_active():
    #     time.sleep(0.001)
    while True:
        continue
time.sleep(5)
# stop_audio(stream_pink, audio_pink)
stop_audio(stream_pseudo, audio_pseudo)


