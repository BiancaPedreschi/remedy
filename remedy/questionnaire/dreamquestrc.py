from psychopy import core, event, visual, sound, gui
from .questlist import questlist
import os
import os.path as op
from datetime import datetime
import numpy as np
import json
import threading
import importlib.util
spec = importlib.util.spec_from_file_location("audio_recorder", op.join(os.getcwd(), 'remedy', 'utils', 'audio_recorder.py'))
audio_recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio_recorder)
start_recording = audio_recorder.start_recording
save_recording_audio = audio_recorder.save_recording_audio

def colored_print(color, text):
    colors = {
        'cyan': '\033[96m',
        'end': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['end']}")

def conv2sec(hours, minutes, seconds):
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

def dreamquestrc(participant_id, session, sex, out_path, fs=44100):
    # win = visual.Window(fullscr=False, color="white", units="norm")

    curr_path = os.path.dirname(os.path.abspath(__file__))
    datapath = os.path.join(curr_path, 'questions_org')
    outpath = os.path.join(out_path, 'recordings', f"participant_{participant_id}", f"session_{session}")
    os.makedirs(outpath, exist_ok=True)

    files = ['qst01', 'qst02_1', 'qst02_2', 'qst02_3', 'qst03', 'qst04', 'qst05', 'qst05_1', 'qst06', 'qst07',
             'qst08', 'qst09', 'qst10', 'qst10_1', 'qst10_2', 'qst10_3', 'qst10_4', 'qst10_5',
             'qst11', 'qst12', 'qst13', 'qst14', 'qst15']
    cmp = {'Female': ['', '', '', '', 'f', 'f', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'f'],
           'Male': ['', '', '', '', 'm', 'm', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'm']}
    questions = {file: sound.Sound(os.path.join(datapath, f"{file}{cmp[sex][nx]}.wav")) for nx, file in enumerate(files)}

    responses = {}
    
    # Configura la registrazione audio
    duration = 3600  # Registra per un'ora (puoi modificare questo valore)
    channels = 2
    device_index = 0  # Assicurati che questo sia l'indice corretto
    recorded_data = []

    print("Inizio del questionario")
    print(f"Partecipante: {participant_id}, Sessione: {session}, Sesso: {sex}")
    print(f"Directory di output: {outpath}")
    print("Premi 'q' in qualsiasi momento per interrompere il questionario e salvare i dati.")


    stop_recording_event = threading.Event()
    recording_thread = threading.Thread(target=start_recording, args=(duration, fs, channels, stop_recording_event, recorded_data, device_index))
    recording_thread.start()

    question_count = 0
    try:
        for qn in range(1, 16):
            sq = f"{qn:02d}"
            colored_print('cyan', f'*** Question {sq} ***')

            # Riproduci l'audio della domanda
            if f'qst{sq}' in questions:
                questions[f'qst{sq}'].play()
                core.wait(questions[f'qst{sq}'].getDuration())
            
            # Controlla se l'utente vuole interrompere
            if event.getKeys(['q']):
                print("Interruzione richiesta dall'utente.")
                break
            
            if qn == 1:
                dlg = gui.Dlg(title=f"Domanda {sq}")
                dlg.addText(questlist(qn))
                dlg.addField('Risposta:', choices=['ER', 'EWR', 'NE'])
                result = dlg.show()
                
                if result[0] == 'ER':
                    responses['qst01'] = 2
                    audio_key = 'qst02_1'
                elif result[0] == 'EWR':
                    responses['qst01'] = 1
                    audio_key = 'qst02_2'
                else:  # NE
                    responses['qst01'] = 0
                    audio_key = 'qst02_3'
                
                # Riproduci l'audio corrispondente
                if audio_key in questions:
                    print(f"Riproducendo audio: {audio_key}")
                    questions[audio_key].play()
                    core.wait(questions[audio_key].getDuration())
                else:
                    print(f"Audio {audio_key} non trovato")
                
                # Gestisci la risposta alla domanda 2 in base alla risposta alla domanda 1
                if result[0] == 'ER':
                    dlg = gui.Dlg(title="Durata")
                    dlg.addField('Ore:')
                    dlg.addField('Minuti:')
                    dlg.addField('Secondi:')
                    duration = dlg.show()
                    # Converti i valori in interi, usando 0 se il campo è vuoto
                    hours = int(duration[0]) if duration[0] else 0
                    minutes = int(duration[1]) if duration[1] else 0
                    seconds = int(duration[2]) if duration[2] else 0
                    responses['qst02'] = conv2sec(hours, minutes, seconds)
                elif result[0] == 'EWR':
                    dlg = gui.Dlg(title=f"Domanda {sq}")
                    dlg.addText(questlist(2_2))
                    dlg.addField('Risposta:', choices=['Sì', 'No'])
                    responses['qst02'] = 1 if dlg.show()[0] == 'Sì' else 0
                elif result[0] == 'NE':
                    dlg = gui.Dlg(title=f"Domanda {sq}")
                    dlg.addText(questlist(2_3))
                    dlg.addField('Risposta:', choices=['Sì', 'No'])
                    responses['qst02'] = 1 if dlg.show()[0] == 'Sì' else 0
                
                # Aggiungi dei print per il debug
                print(f"Risposta alla domanda 1: {responses['qst01']}")
                print(f"Risposta alla domanda 2: {responses['qst02']}")

                if qn >= 5:
                    break
            elif qn in [3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 15]:
                dlg = gui.Dlg(title=f"Domanda {sq}")
                dlg.addText(questlist(qn))
                dlg.addField('Risposta:', choices=['1', '2', '3', '4', '5'])
                responses[f'qst{sq}'] = int(dlg.show()[0])
            elif qn == 5:
                dlg = gui.Dlg(title=f"Domanda {sq}")
                dlg.addText(questlist(qn))
                dlg.addField('Risposta:', choices=['Sì', 'No'])
                responses['qst05'] = 1 if dlg.show()[0] == 'Sì' else 0
                if responses['qst05'] == 1:
                    dlg = gui.Dlg(title="Tipo di stimolo")
                    dlg.addField('Descrizione:')
                    responses['qst05_desc'] = dlg.show()[0]
            elif qn == 10:
                responses['qst10'] = np.full((1, 5), np.nan)
                sensi = ['Visivo', 'Uditivo', 'Tattile', 'Olfattivo', 'Gustativo']
                for ns, senso in enumerate(sensi, start=1):
                    questions[f'qst10_{ns}'].play()
                    core.wait(questions[f'qst10_{ns}'].getDuration())
                    dlg = gui.Dlg(title=f"Domanda 10.{ns}: {senso}")
                    dlg.addText(f"Hai avuto un'esperienza {senso.lower()}?")
                    dlg.addField('Risposta:', choices=['Sì', 'No'])
                    responses['qst10'][0, ns - 1] = 1 if dlg.show()[0] == 'Sì' else 0
            
            question_count += 1
            print(f"Domanda {sq} completata")
            print(f"Risposta salvata: {responses.get(f'qst{sq}', 'Non disponibile')}")

        print(f"Totale domande presentate: {question_count}")

    except Exception as e:
        print(f"Si è verificato un errore: {e}")
    finally:
        # Ferma la registrazione
        stop_recording_event.set()
        recording_thread.join()

        # Salva la registrazione audio
        if recorded_data:
            try:
                audio_file = save_recording_audio(recorded_data[0], outpath, participant_id, session, fs)
                if audio_file and os.path.exists(audio_file):
                    print(f"File audio creato: {audio_file}")
                else:
                    print(f"Errore: File audio non creato o non trovato. Percorso atteso: {audio_file}")
            except Exception as e:
                print(f"Errore durante il salvataggio dell'audio: {e}")
        else:
            print("Nessun dato registrato.")

        cdate = datetime.now().strftime("%Y-%m-%d")
        ctime = datetime.now().strftime("%H:%M:%S")

    data_to_save = {
        "cdate": cdate,
        "ctime": ctime,
        "participant_id": participant_id,
        "session": session,
        "sex": sex,
        "responses": {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in responses.items()}
    }
    foutname = os.path.join(outpath, f"dati_{participant_id}_{session}.json")
    with open(foutname, 'w') as json_file:
        json.dump(data_to_save, json_file, indent=4)

    if os.path.exists(foutname):
        print(f"File JSON creato: {foutname}")
    else:
        print("Errore: File JSON non creato")

        core.quit()

if __name__ == "__main__":
    dreamquestrc()

# dreamquestrc("001", 1, "Female", "./output", fs=48000)