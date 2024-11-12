import numpy as np
from scipy import signal
import scipy.io.wavfile as sw
import soundfile as sf
import matplotlib.pyplot as plt

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
output_file = "PN_1.wav"
sf.write(output_file, pink_noise, sample_rate)
# sw.write(output_file, sample_rate, pink_noise)

print(f"File di pink noise generato: {output_file}")

# Genera il pink noise
a_shuffled = [1.5, 2.3, 1.9, 1.8, 1.7, 2.2, 2.4, 2., 2.1, 1.6, 2.5]
# duration = 60  # 1 minuto per esempio
sample_rate = 44100
for i in range(len(a_shuffled)):
    duration = a_shuffled[i]
    pink_noise = generate_pink_noise(duration, sample_rate)
    output_file = f"PN_{duration}s_{i+1}.wav"
    sf.write(output_file, pink_noise, sample_rate)
    # Calcola la densità spettrale di potenza
    frequencies, power_spectral_density = signal.welch(pink_noise, sample_rate, nperseg=1024)

# Plotta lo spettro di frequenza
plt.figure(figsize=(10, 6))
plt.semilogx(frequencies, 10 * np.log10(power_spectral_density))
plt.title('Densità spettrale di potenza del Pink Noise')
plt.xlabel('Frequenza [Hz]')
plt.ylabel('Densità spettrale di potenza [dB/Hz]')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.show()