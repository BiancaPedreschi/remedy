import os 
import numpy as np
import scipy.io.wavfile as wav

def apply_fade(signal, fade_in_duration, fade_out_duration, srate):
    n_samples = len(signal)
    fade_in_samples = int(srate * fade_in_duration)
    fade_out_samples = int(srate * fade_out_duration)

    # Crea fade-in
    fade_in = np.linspace(0, 1, fade_in_samples)
    signal[:fade_in_samples] *= fade_in

    # Crea fade-out
    fade_out = np.linspace(1, 0, fade_out_samples)
    signal[-fade_out_samples:] *= fade_out

    return signal

def two_sinusoids(duration, f0, f1, srate, a=1, phi=0):
    t = np.linspace(0., duration, int(np.floor(srate * duration)))
    cos1 = np.cos(2 * np.pi * f0 * t)
    cos2 = np.cos(2 * np.pi * f1 * t + phi)
    two_freqs = cos1 + (a * cos2)
    
    return two_freqs

if __name__ == '__main__':
    duration = 2.
    srate = 44100
    # f0 = [110, 220, 330, 440, 550, 660, 770, 880]
    f0 = np.arange(55, 881, 55)
    # alpha = [1.001, 1.01, 1.05, 1.1, 1.3, 1.4, 1.6, 1.8, 2.0]
    # alpha = [1.6, 1.7, 1.8, 1.9, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    # alpha = np.arange(1.6, 5.1, 0.2).round(1)
    alpha = np.arange(.5, 5.6, 0.5).round(1)
    fade_in_duration = .5  # Durata del fade-in in secondi
    fade_out_duration = .5  # Durata del fade-out in secondi
    output_dir = "sounds_2sec_v1"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for _f in f0:
        for _a in alpha:
            two_freqs = two_sinusoids(duration, _f, _f*_a, srate)
            two_freqs = apply_fade(two_freqs, fade_in_duration, fade_out_duration, srate)
            filename = f"{output_dir}/tone_{_f}_{_a}.wav"
            wav.write(filename, srate, two_freqs.astype(np.float32))