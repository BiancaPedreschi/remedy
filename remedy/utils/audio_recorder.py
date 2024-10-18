import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import os.path as op
import time
        
        
def start_recording(duration, fs=44100, channels=2, stop_event=None, 
                    recording_container=None, device_index=5):
    """Inizia la registrazione audio e ritorna l'array numpy con i dati."""
    
    answ = np.full((duration * fs, 1), np.nan)
    sd.default.device = device_index
    try:
        # sd.rec(channels=1, dtype='float32')
        print(f"Configurazione della registrazione: durata={duration}, fs={fs}, channels={channels}, device_index={device_index}")
        data = sd.rec(samplerate=44100, channels=1, dtype='int16', out=answ)
    except Exception as e:
        print(f"Errore durante la registrazione: {e}")
        
    recording_container.append(data)
        
    return recording_container
        
        
def save_recording_audio(recording, output_directory, subject_id, session, 
                         cdate, ctime, fs=44100):
    """Salva la registrazione in un file WAV con un nome personalizzato."""
    if recording.size > 0:  # Controlla se l'array contiene dati
        filename = op.join(output_directory, 
                           f'RY{subject_id:03d}_N{session}_{cdate}_{ctime}.wav')
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


def test():
    stop_event = threading.Event()
    recorded_data = [] 
    device_index = 0  # Assicurati che questo sia l'indice corretto

    sd.default.device = 5
    snd = np.random.uniform(0, 1, (10*44100, 2))
    snd /= np.max(np.abs(snd))
    sd.play(snd)
    # Avvia la registrazione in un thread separato
    recording_thread = threading.Thread(target=start_recording, 
                                        args=(10, 44100, 2, stop_event, 
                                              recorded_data, device_index))
    recording_thread.start()
    time.sleep(10)

    # Per fermare la registrazione
    stop_event.set()
    recording_thread.join()

    # Ora recorded_data contiene i dati della registrazione
    if recorded_data:
        save_recording_audio(recorded_data[0], "/home/phantasos/Scrivania", 
                             "subject_id", "session_id")
    else:
        print("Nessun dato registrato.")

if __name__ == "__main__":
    test()