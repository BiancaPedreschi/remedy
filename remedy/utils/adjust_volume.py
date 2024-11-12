import sounddevice as sd
import soundfile as sf
from remedy.config.config import read_config
import os
import os.path as op
from remedy.utils.find_devices import find_device

# def adjust_volume(orig_PN, orig_PP, new_PN, new_PP, volume_PN=1, volume_PP=1, fs=44100):
#     for opn, npn in zip(orig_PN, new_PN):
#         print(f"Processing file: {opn}") 
#         _opn = sf.read(opn)[0]
#         _npn = _opn * volume_PN
#         # sd.play(_npn)
#         # sd.wait()
#         sf.write(npn, _npn, fs)
#     for opp, npp in zip(orig_PP, new_PP):
#         print(f"Processing file: {opp}") 
#         _opp = sf.read(opp)[0]
#         _npp = _opp * volume_PP
#          # sd.play(_npp)
#          # sd.wait()
#         sf.write(npp, _npp, fs)
def adjust_volume(orig_PN, new_PN, volume_PN=1, fs=44100):
    for opn, npn in zip(orig_PN, new_PN):
        print(f"Processing file: {opn}") 
        _opn = sf.read(opn)[0]
        _npn = _opn * volume_PN
        # sd.play(_npn)
        # sd.wait()
        sf.write(npn, _npn, fs)
<<<<<<< HEAD
=======
    for opp, npp in zip(orig_PP, new_PP):
        _opp = sf.read(opp)[0]
        _npp = _opp * volume_PP
        # sd.play(_npp)
        # sd.wait()
        sf.write(npp, _npp, fs)
>>>>>>> 35b80a28a7592b0742714c090b99679ac7be9572
    
    return

if __name__ == "__main__":
    # Define paths and stimuli
    config = read_config()
    data_dir = config['paths']['data']
    PP_letters = ['A', 'B', 'C', 'D', 'E', 'F']
    PN_segments_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'L', 'M']
    
    # Change volume for night stimuli
<<<<<<< HEAD
    # orig_fname_PN = [op.join(data_dir, 'pwd_originals', 'night_stim', 'PN.wav')]
    # orig_fname_PP = [op.join(data_dir, 'pwd_originals', 'day_stim', f'pseudoparola_{fn}.wav') for fn in PP_letters]
    # new_fname_PN = [op.join(data_dir, 'pwd', 'night_stim', 'PN_1.wav')]
    # new_fname_PP = [op.join(data_dir, 'pwd', 'night_stim', f'pseudoparola_{fn}.wav') for fn in PP_letters]
    # # # dev_hp, dev_sp = find_device()
    # # # sd.default.device = dev_hp
    # adjust_volume(orig_fname_PN, orig_fname_PP, new_fname_PN, new_fname_PP, volume_PN=.7, volume_PP=0.004)
    
    # # Change volume for day stimuli
    # orig_fname_PN = [op.join(data_dir, 'pwd_originals', 'day_stim', 'PN.wav')]
    # orig_fname_PP = [op.join(data_dir, 'pwd_originals', 'day_stim', f'pseudoparola_{fn}.wav') for fn in PP_letters]
    # new_fname_PN = [op.join(data_dir, 'pwd', 'day_stim', 'PN.wav')]
    # new_fname_PP = [op.join(data_dir, 'pwd', 'day_stim', f'pseudoparola_{fn}.wav') for fn in PP_letters]
    # # dev_hp, dev_sp = find_device()
    # # sd.default.device = dev_hp
=======
    orig_fname_PN = [op.join(data_dir, 'pwd_originals', 'night_stim', 'PN.wav')]
    orig_fname_PP = [op.join(data_dir, 'pwd_originals', 'night_stim', f'pseudoparola_{fn}.wav') for fn in PP_letters]
    new_fname_PN = [op.join(data_dir, 'pwd', 'night_stim', 'PN.wav')]
    new_fname_PP = [op.join(data_dir, 'pwd', 'night_stim', f'pseudoparola_{fn}.wav') for fn in PP_letters]
    dev_hp, dev_sp = find_device()
    sd.default.device = dev_hp
    adjust_volume(orig_fname_PN, orig_fname_PP, new_fname_PN, new_fname_PP, volume_PN=.07, volume_PP=.04)
    
    # Change volume for day stimuli
    orig_fname_PN = [op.join(data_dir, 'pwd_originals', 'day_stim', 'PN.wav')]
    orig_fname_PP = [op.join(data_dir, 'pwd_originals', 'day_stim', f'pseudoparola_{fn}.wav') for fn in PP_letters]
    new_fname_PN = [op.join(data_dir, 'pwd', 'day_stim', 'PN.wav')]
    new_fname_PP = [op.join(data_dir, 'pwd', 'day_stim', f'pseudoparola_{fn}.wav') for fn in PP_letters]
    dev_hp, dev_sp = find_device()
    sd.default.device = dev_hp
    adjust_volume(orig_fname_PN, orig_fname_PP, new_fname_PN, new_fname_PP, volume_PN=.0, volume_PP=.5)
>>>>>>> 35b80a28a7592b0742714c090b99679ac7be9572
    # adjust_volume(orig_fname_PN, orig_fname_PP, new_fname_PN, new_fname_PP, volume_PN=.2, volume_PP=.2)
    
    # Directory dei file originali e modificati
    orig_dir = op.join(data_dir, 'pwd_originals', 'PN_segments')
    new_dir = op.join(data_dir, 'pwd', 'PN_segments')

    # Ottieni i nomi dei file dalla directory originale
    orig_fnames_PNs = [op.join(orig_dir, file) for file in os.listdir(orig_dir) if file.endswith('.wav')]
    new_fnames_PNs = [op.join(new_dir, file) for file in os.listdir(orig_dir) if file.endswith('.wav')]
    # dev_hp, dev_sp = find_device()
    # sd.default.device = dev_hp
    adjust_volume(orig_fnames_PNs, new_fnames_PNs, volume_PN=2)
    
