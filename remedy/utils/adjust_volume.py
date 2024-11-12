import sounddevice as sd
import soundfile as sf
from remedy.config.config import read_config
import os.path as op
from remedy.utils.find_devices import find_device

def adjust_volume(orig_PN, orig_PP, new_PN, new_PP, volume_PN=1, volume_PP=1, fs=44100):
    for opn, npn in zip(orig_PN, new_PN):
        _opn = sf.read(opn)[0]
        _npn = _opn * volume_PN
        # sd.play(_npn)
        # sd.wait()
        sf.write(npn, _npn, fs)
    for opp, npp in zip(orig_PP, new_PP):
        _opp = sf.read(opp)[0]
        _npp = _opp * volume_PP
        # sd.play(_npp)
        # sd.wait()
        sf.write(npp, _npp, fs)
    
    return

if __name__ == "__main__":
    # Define paths and stimuli
    config = read_config()
    data_dir = config['paths']['data']
    PP_letters = ['A', 'B', 'C', 'D', 'E', 'F']
    
    # Change volume for night stimuli
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
    # adjust_volume(orig_fname_PN, orig_fname_PP, new_fname_PN, new_fname_PP, volume_PN=.2, volume_PP=.2)
    
    
