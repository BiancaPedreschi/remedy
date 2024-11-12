import pyaudio
import wave
import threading
from psychopy import visual, core, event
import random

# Funzione per riprodurre un file audio
def play_audio(file_path, volume=1.0):
    def callback(in_data, frame_count, time_info, status):
        data = wf.readframes(frame_count)
        return (data, pyaudio.paContinue)

    wf = wave.open(file_path, 'rb')
    p = pyaudio.PyAudio()
    # stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
    #                 channels=wf.getnchannels(),
    #                 rate=wf.getframerate(),
    #                 output=True,
    #                 stream_callback=callback,
    #                 output_device_index=4)
    info = p.get_device_info_by_index(8)
    stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=int(info['defaultSampleRate']),
                    output=True,
                    stream_callback=callback,
                    frames_per_buffer=1024,
                    output_device_index=8)
    stream.start_stream()
    return stream, p

# Funzione per interrompere lo stream audio
def stop_audio(stream, p):
    stream.stop_stream()
    stream.close()
    p.terminate()

# Carica i file audio di esempio
pink_noise_file = "/home/phantasos/python_projects/space/remedy/data/pwd/night_stim/PN.wav"
other_audio_file = "/home/phantasos/python_projects/space/remedy/data/pwd/night_stim/pseudoparola_A.wav"
# other_audio_file = "/Users/foscagiannotti/Desktop/python_projects/space/remedy/data/remedy_data/pwd/PP_A.wav"
# Crea una finestra PsychoPy
win = visual.Window(fullscr=False, color="black", units="norm")

# Riproduci il pink noise in loop
pink_noise_stream, pink_noise_p = play_audio(pink_noise_file)
for i in range(5):
    intrstimulus = random.uniform(1.5, 2.5)
    core.wait(intrstimulus)

    # Riproduci un altro file audio contemporaneamente
    other_audio_stream, other_audio_p = play_audio(other_audio_file)


# Mostra un messaggio e attendi un tasto per uscire
message = visual.TextStim(win, text="Premi un tasto per uscire", pos=(0, 0), height=0.1, units='norm', color='white')
message.draw()
win.flip()
event.waitKeys()

# Interrompi gli stream audio e chiudi la finestra
stop_audio(pink_noise_stream, pink_noise_p)
stop_audio(other_audio_stream, other_audio_p)


def list_audio_devices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"Device {i}: {info['name']}")
    p.terminate()

print(list_audio_devices())
win.close()
core.quit()