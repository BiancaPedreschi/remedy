import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import os
import time

# def start_recording(duration, fs=44100, channels=2, stop_event=None, recording_container=None, device_index=5):
#     """Inizia la registrazione audio e ritorna l'array numpy con i dati."""
#     try:
#         print(f"Configurazione della registrazione: durata={duration}, fs={fs}, channels={channels}, device_index={device_index}")
#         with sd.InputStream(samplerate=fs, channels=channels, dtype='float32', device=device_index) as stream:
#             recording = []
#             print("Inizio registrazione")
#             for _ in range(int(duration * fs / 1024)):
#                 data, overflowed = stream.read(1024)
#                 if stop_event.is_set():
#                     print("Interruzione anticipata")
#                     break
#                 recording.append(data)
#             if len(recording) > 0:  # Usa len() per verificare se la lista è vuota
#                 complete_recording = np.concatenate(recording, axis=0)
#                 recording_container.append(complete_recording)
#                 print("Registrazione aggiunta al contenitore, forma:", complete_recording.shape)
#             else:
#                 print("Nessun dato registrato")
#     except Exception as e:
#         print(f"Errore durante la registrazione: {e}")

# def save_recording_pseudowords(recording, output_directory, subject_id, session, fs=44100):
#     """Salva la registrazione in un file WAV con un nome personalizzato."""
#     if recording.size > 0:  # Controlla se l'array contiene dati
#         if not os.path.exists(output_directory):
#             os.makedirs(output_directory)
#         filename = f"{output_directory}/recall_pseudowards_{subject_id}_{session}.wav"
#         print(f"Tentativo di salvataggio in: {filename}")  # Stampa il percorso del file
#         sf.write(filename, recording, fs)
#         print(f"Registrazione salvata in: {filename}")
#     else:
#         print("Nessun dato da salvare.")

# def save_recording_audio(recording, output_directory, subject_id, session, fs=44100):
#     """Salva la registrazione in un file WAV con un nome personalizzato."""
#     if recording.size > 0:  # Controlla se l'array contiene dati
#         if not os.path.exists(output_directory):
#             os.makedirs(output_directory)
#         filename = f"{output_directory}/awakeing_pp{subject_id}_sess{session}_time{time.strftime('%Y%m%d_%H%M%S')}.wav"
#         print(f"Tentativo di salvataggio in: {filename}")  # Stampa il percorso del file
#         try:
#             sf.write(filename, recording, fs)
#             print(f"Registrazione salvata in: {filename}")
#             return filename
#         except Exception as e:
#             print(f"Errore durante il salvataggio del file audio: {e}")
#             return None
#     else:
#         print("Nessun dato da salvare.")
#         return None
    
    
def start_recording(duration, fs=44100, channels=2, stop_event=None, recording_container=None, device_index=5):
    """Inizia la registrazione audio e ritorna l'array numpy con i dati."""
    
    try:
        # sd.rec(channels=1, dtype='float32')
        print(f"Configurazione della registrazione: durata={duration}, fs={fs}, channels={channels}, device_index={device_index}")
        with sd.Stream(samplerate=44100, channels=1, dtype='float32', device=5) as stream:
            recording = []
            print("Inizio registrazione")
            for _ in range(int(duration * fs / 1024)):
                data, overflowed = stream.read(1024)
                if stop_event.is_set():
                    print("Interruzione anticipata")
                    break
                recording.append(data)
            if len(recording) > 0:  # Usa len() per verificare se la lista è vuota
                complete_recording = np.concatenate(recording, axis=0)
                recording_container.append(complete_recording)
                print("Registrazione aggiunta al contenitore, forma:", complete_recording.shape)
            else:
                print("Nessun dato registrato")
    except Exception as e:
        print(f"Errore durante la registrazione: {e}") 
        
        
def save_recording_audio(recording, output_directory, subject_id, session, fs=44100):
    """Salva la registrazione in un file WAV con un nome personalizzato."""
    if recording.size > 0:  # Controlla se l'array contiene dati
        # if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)
        filename = f"{output_directory}/awakeing_pp{subject_id}_sess{session}_time{time.strftime('%Y%m%d_%H%M%S')}.wav"
        print(f"Tentativo di salvataggio in: {filename}")  # Stampa il percorso del file
        try:
            sf.write(filename, recording, fs)
            print(f"Registrazione salvata in: {filename}")
            return filename
        except Exception as e:
            print(f"Errore durante il salvataggio del file audio: {e}")
            return None
    else:
        print("Nessun dato da salvare.")
        return None   


# # Utilizzo
# stop_event = threading.Event()
# recorded_data = [] 
# device_index = 0  # Assicurati che questo sia l'indice corretto

# # Avvia la registrazione in un thread separato
# recording_thread = threading.Thread(target=start_recording, args=(10, 44100, 2, stop_event, recorded_data, device_index))
# recording_thread.start()

# # Per fermare la registrazione
# stop_event.set()
# recording_thread.join()

# # Ora recorded_data contiene i dati della registrazione
# if recorded_data:
#     save_recording_audio(recorded_data[0], "/Users/foscagiannotti/Desktop/python_projects/space/remedy/data/output_wake", "subject_id", "session_id")
# else:
def test():
    stop_event = threading.Event()
    recorded_data = [] 
    device_index = 0  # Assicurati che questo sia l'indice corretto

    sd.default.device = 5
    snd = np.random.uniform(0, 1, (10*44100, 2))
    snd /= np.max(np.abs(snd))
    sd.play(snd)
    # Avvia la registrazione in un thread separato
    recording_thread = threading.Thread(target=start_recording, args=(10, 44100, 2, stop_event, recorded_data, device_index))
    recording_thread.start()
    time.sleep(10)

    # Per fermare la registrazione
    stop_event.set()
    recording_thread.join()

    # Ora recorded_data contiene i dati della registrazione
    if recorded_data:
        save_recording_audio(recorded_data[0], "/home/phantasos/Scrivania", "subject_id", "session_id")
    else:
        print("Nessun dato registrato.")

if __name__ == "__main__":
    test()