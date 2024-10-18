import threading
import time
# from utils.audio_recorder import start_recording, save_recording_audio
from remedy.utils.audio_recorder import start_recording, save_recording_audio

# Configurazione iniziale
duration = 10  # durata della registrazione in secondi
fs = 44100  # frequenza di campionamento
channels = 1  # numero di canali
device_index = 4  # indice del dispositivo (0 per il microfono integrato)
output_directory = "/home/phantasos/Scrivania"
subject_id = "example_subject"
session_id = "example_session"

# Contenitore per i dati registrati
recorded_data = []
stop_recording_event = threading.Event()

# Avvia la registrazione in un thread separato
recording_thread = threading.Thread(target=start_recording, args=(duration, fs, channels, stop_recording_event, recorded_data, device_index))
recording_thread.start()

# Aggiungi un ritardo prima di impostare l'evento di stop per testare
time.sleep(10)  # Aspetta 10 secondi prima di fermare la registrazione

# Fermare la registrazione e salvare i dati
stop_recording_event.set()
recording_thread.join()

if recorded_data:
    save_recording_audio(recorded_data[0], output_directory, subject_id, session_id, fs)
else:
    print("Nessun dato è stato registrato dopo l'attesa.")