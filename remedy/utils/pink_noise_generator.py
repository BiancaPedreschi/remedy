import numpy as np
from scipy import signal
import soundfile as sf

def generate_pink_noise(duration, sample_rate=44100):
    samples = int(duration * sample_rate)
    
    # Genera rumore bianco
    white_noise = np.random.normal(0, 1, samples)
    
    # Crea il filtro per il pink noise
    b, a = signal.butter(1, 1.0, btype='lowpass', fs=sample_rate)
    
    # Applica il filtro per ottenere il pink noise
    pink_noise = signal.lfilter(b, a, white_noise)
    
    # Normalizza
    pink_noise = pink_noise / np.max(np.abs(pink_noise))
    
    return pink_noise

# Genera 10 minuti di pink noise
duration = 60 * 60# 20 minuti in secondi
sample_rate = 44100
pink_noise = generate_pink_noise(duration, sample_rate)

# Salva il file audio
output_file = "pink_noise_60min.wav"
sf.write(output_file, pink_noise, sample_rate)

print(f"File di pink noise generato: {output_file}")