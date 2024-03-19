
import psychtoolbox as ptb
from psychopy import core, event, visual, microphone, sound, gui
import cprintf
import questlist
import os
from datetime import datetime
import numpy as np
import json
import shutil


def initialize_audio(device_id, fs, volume=0.5):
    # Apri il dispositivo audio specificato
    pahandle = ptb.PsychPortAudio('Open', device_id, [], 1, fs, 1)
    # Imposta il volume del dispositivo audio
    ptb.PsychPortAudio('Volume', pahandle, volume)
    return pahandle


def start_recording(fs, saveDir='.'):
    """
    Avvia la registrazione audio che continuerà per tutta la durata del questionario.
    """
    microphone.switchOn(sampleRate=fs)
    mic = microphone.AdvAudioCapture(name='questionario_completo', saveDir=saveDir, stereo=False, sampleRate=fs)
    mic.record(sec=0, block=False)  # sec=0 per una registrazione continua
    return mic


def stop_recording(mic, recout):
    """
    Ferma la registrazione audio e salva il file nel percorso specificato.
    """
    mic.stop()
    final_path = os.path.join(recout, mic.savedFile)
    shutil.move(mic.savedFile, final_path)
    return final_path


def conv2sec(hours, minutes, seconds):
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    return total_seconds


def dreamquestrc(participant_id, session, sex, out_path, n_quest, fs=48000):
    # Configura il microfono in Psychopy
    microphone.switchOn(sampleRate=fs)

    # Definisce i percorsi per i file audio delle domande e per le registrazioni
    curr_path = os.path.dirname(os.path.abspath(__file__))
    datapath = os.path.join(curr_path, 'questions_org')
    outpath = os.path.join(out_path, 'recordings')

    # Lista dei file audio e mappa il sesso del partecipante ai suffissi dei file audio specifici
    files = ['qst01', 'qst02_1', 'qst02_2', 'qst02_3', 'qst03', 'qst04', 'qst05', 'qst05_1', 'qst06', 'qst07',
             'qst08', 'qst08_1', 'qst08_2', 'qst08_3', 'qst08_4', 'qst08_5', 'qst09', 'qst10',
             'qst11', 'qst12', 'qst13', 'qst14', 'qst15']

    cmp = {'Female': ['', '', '', '', 'f', 'f', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'f'],
           'Male': ['', '', '', '', 'm', 'm', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'm']}

    print(f'Selected gender: {sex}')

    # Carica i file audio delle domande in base al sesso del partecipante
    questions = {}
    for nx, file in enumerate(files):
        fname = f"{file}{cmp[sex][nx]}.wav"
        questions[file] = sound.Sound(os.path.join(datapath, fname))

    print('Questions loaded')

    # ____ Prepara la directory di output per salvare le registrazioni
    # Impostazioni iniziali
    cdate = datetime.now().strftime("%Y-%m-%d")
    ctime = datetime.now().strftime("%H:%M:%S")

    # Formatta il numero della domanda per garantire che abbia sempre due cifre
    s_quest = f"{n_quest:02}"

    outpath = os.path.join(out_path, 'recordings', f"participant_{participant_id}", f"session_{session}")
    os.makedirs(outpath, exist_ok=True)

    # Inizializzazione di responses e recordings
    responses = {}
    recordings = {}

    # Avvia la registrazione audio all'inizio del questionario
    mic = start_recording(fs, saveDir=outpath)

    # ____Loop per ogni domanda
    flagbrk = 0  # Flag per interrompere il questionario se NE o EWR
    for qn in range(1, 16):
        if qn < 10:
            sq = '0' + str(qn)
        else:
            sq = str(qn)

        cprintf('cyan', f'*** Question {sq} ***')
        answ = input(
            'Question ' + sq + ': ER (experience + recall), EWR (experience + no-recall), NE (no-experience): ')

        if qn != 2:
            # Carica il buffer audio
            buffer_audio = questions['qst' + sq]
            asamples = len(buffer_audio)

            # Stampa la domanda
            print(questlist(qn))

        # Case 2
        if qn == 1:
            qstring = questlist(qn)
            print(qstring)
            if answ == 'ER':
                responses['qst01'] = 2
            elif answ == 'EWR':
                responses['qst01'] = 1
                flagbrk = 1
            elif answ == 'NE':
                responses['qst01'] = 0
                flagbrk = 1

            if responses['qst01'] == 2:
                hours = input('inserisci ore: ')
                minutes = input('inserisci minuti: ')
                seconds = input('inserisci secondi: ')
                answ = (hours, minutes, seconds)
                # recout = f'{outpath}/{pathname}/{cdate}-{numrec}-{sq}.wav'
                # recordings['qst02'] = record_audio(fs, rec_duration)
                responses['qst02'] = conv2sec(answ)
            elif responses['qst01'] == 1:
                answ = input('Question ' + sq + ': Yes or No? ')
                # recout = f'{outpath}/{pathname}/{cdate}-{numrec}-{sq}.wav'
                # recordings['qst02'] = record_audio(fs, rec_duration)
                if answ == 'Yes':
                    responses['qst02'] = 1
                elif answ == 'No':
                    responses['qst02'] = 0
            elif responses['qst01'] == 0:
                answ = input('Question ' + sq + ': Yes or No? ')
                # recout = f'{outpath}/{pathname}/{cdate}-{numrec}-{sq}.wav'
                # recordings['qst02'] = record_audio(fs, rec_duration)
                if answ == 'Yes':
                    responses['qst02'] = 1
                elif answ == 'No':
                    responses['qst02'] = 0

        # Case 3
        elif qn == 3:
            # Creazione di una dialog box con PsychoPy
            dlg = gui.Dlg(title=f"Domanda {sq}")
            dlg.addText("Quanto profondamente ti sentivi addormentato/a prima del suono della sveglia?")
            dlg.addField('Risposta:', choices=['1', '2', '3', '4', '5'])
            dlgResult = dlg.show()
            if dlg.OK:
                responses['qst03'] = int(dlgResult[0])
            else:
                responses['qst03'] = None

        # Case 4
        elif qn == 4:
            # Creazione di una dialog box con PsychoPy
            dlg = gui.Dlg(title=f"Domanda {sq}")
            dlg.addText("Quanto ti senti stanco?")
            dlg.addField('Risposta:', choices=['1', '2', '3', '4', '5'])
            dlgResult = dlg.show()
            if dlg.OK:
                responses['qst04'] = int(dlgResult[0])
            else:
                responses['qst04'] = None

        # Case 5
        elif qn == 5:
            dlg = gui.Dlg(title=f"Domanda {sq}")
            dlg.addText("Ritieni di aver percepito uno stimolo poco prima del suono della sveglia?")
            dlg.addField('Risposta:', choices=['Sì', 'No'])
            dlgResult = dlg.show()
            if dlgResult[0] == 'Sì':
                # Qui potresti voler fare ulteriori domande per specificare il tipo di stimolo
                responses['qst05'] = 1
            else:
                responses['qst05'] = 0

        # Case 6
        elif qn == 6:
            dlg = gui.Dlg(title=f"Domanda {sq}")
            dlg.addText("Quanto era vivida l’esperienza?")
            dlg.addField('Risposta:', choices=['1', '2', '3', '4', '5'])
            dlgResult = dlg.show()
            if dlg.OK:
                responses['qst06'] = int(dlgResult[0])
            else:
                responses['qst06'] = None

        # Case 7
        elif qn == 7:
            dlg = gui.Dlg(title=f"Domanda {sq}")
            dlg.addText("Quanto l’esperienza era percettiva piuttosto che in forma di pensiero ")
            dlg.addField('Risposta:', choices=['1', '2', '3', '4', '5'])
            dlgResult = dlg.show()
            if dlg.OK:
                responses['qst07'] = int(dlgResult[0])
            else:
                responses['qst07'] = None

        # Caso 8
        elif qn == 8:
            sensi = ['Visivo', 'Uditivo', 'Tattile', 'Olfattivo',
                     'Gustativo']  # domande specifiche per esperienze sensoriali
            responses['qst08'] = np.full((1, 5), np.nan)  # Inizializza le risposte con NaN
            for ns, senso in enumerate(sensi, start=1):  # loop attraverso le domande per le esperienze sensoriali
                # Riproduci il file audio corrispondente alla domanda
                audio_question = sound.Sound(os.path.join(datapath, f'qst08_{ns}.wav'))
                audio_question.play()
                core.wait(audio_question.getDuration())  # Aspetta che finisca la riproduzione dell'audio

                # Presenta la domanda e raccogli la risposta
                dlg = gui.Dlg(title=f"Domanda 8.{ns}: {senso}")
                dlg.addText(f"Hai avuto un'esperienza {senso.lower()}?")
                dlg.addField('Risposta:', choices=['Sì', 'No'])
                dlgResult = dlg.show()
                if dlgResult[0] == 'Sì':
                    responses['qst08'][0, ns - 1] = 1
                else:
                    responses['qst08'][0, ns - 1] = 0

        # Caso 9
        elif qn == 9:
            dlg = gui.Dlg(title=f"Domanda {sq}")
            dlg.addText("Quanto l’esperienza era riconducibile a elementi, situazioni o eventi realmente incontrati?")
            dlg.addField('Risposta:', choices=['1', '2', '3', '4', '5'])
            dlgResult = dlg.show()
            if dlg.OK:
                responses['qst09'] = int(dlgResult[0])
            else:
                responses['qst09'] = None

        # Case 10
        elif qn == 10:
            dlg = gui.Dlg(title=f"Domanda {sq}")
            dlg.addText("Quanto era bizzarra l’esperienza?")
            dlg.addField('Risposta:', choices=['1', '2', '3', '4', '5'])
            dlgResult = dlg.show()
            if dlg.OK:
                responses['qst10'] = int(dlgResult[0])
            else:
                responses['qst10'] = None

        # Caso 11
        elif qn == 11:
            dlg = gui.Dlg(title=f"Domanda {sq}")
            dlg = dlg.addText("Quanto eri consapevole del fatto che l’esperienza non era reale")
            dlg.addField('Risposta:', choices=['1', '2', '3', '4', '5'])
            if dlg.OK:
                responses['qst11'] = int(dlgResult[0])
            else:
                responses['qst11'] = None

        # Caso 12
        elif qn == 12:
            dlg = gui.Dlg(title=f"Domanda {sq}")
            dlg = dlg.addText("Quanto controllo volontario avevi sul contenuto e sullo svolgimento dell’esperienza? ")
            dlg.addField('Risposta:', choices=['1', '2', '3', '4', '5'])
            if dlg.OK:
                responses['qst12'] = int(dlgResult[0])
            else:
                responses['qst12'] = None

        # Caso 13
        elif qn == 13:
            dlg = gui.Dlg(title=f"Domanda {sq}")
            dlg = dlg.addText("Come valuti la valenza emotiva dell’esperienza?")
            dlg.addField('Risposta:', choices=['1', '2', '3', '4', '5'])
            if dlg.OK:
                responses['qst13'] = int(dlgResult[0])
            else:
                responses['qst13'] = None

        # Caso 14
        elif qn == 14:
            dlg = gui.Dlg(title=f"Domanda {sq}")
            dlg = dlg.addText("Come valuti l’intensità emotiva dell’esperienza?")
            dlg.addField('Risposta:', choices=['1', '2', '3', '4', '5'])
            if dlg.OK:
                responses['qst14'] = int(dlgResult[0])
            else:
                responses['qst14'] = None


        # Caso 15
        elif qn == 15:
            dlg = gui.Dlg(title=f"Domanda {sq}")
            dlg = dlg.addText("Quanto ti senti sicuro/a che i ricordi dell’esperienza siano completi e accurati?")
            dlg.addField('Risposta:', choices=['1', '2', '3', '4', '5'])
            if dlg.OK:
                responses['qst15'] = int(dlgResult[0])
            else:
                responses['qst15'] = None

        # Interruzione del questionario alla domanda 5 se la condizione è soddisfatta
        if flagbrk == 1 and qn >= 5:
            break

        # Pulizia della variabile di iterazione del ciclo
        qn = None

    # Ferma la registrazione alla fine del questionario e salva il file audio
    recout = os.path.join(outpath, f"registrazione_{participant_id}_{session}_{cdate}_{ctime}.wav")
    recording_path = stop_recording(mic, recout)

    # Salva i dati del questionario in un file JSON, includendo cdate e ctime
    data_to_save = {
        "cdate": cdate,
        "ctime": ctime,
        "participant_id": participant_id,
        "session": session,
        "sex": sex,
        "recording": recording_path
        # Aggiungi qui altre informazioni raccolte durante il questionario
    }
    foutname = os.path.join(outpath, f"dati_{participant_id}_{session}.json")
    with open(foutname, 'w') as json_file:
        json.dump(data_to_save, json_file, indent=4)
