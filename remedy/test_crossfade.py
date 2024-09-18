import os
import numpy as np
import soundfile as sf
import sounddevice as sd
import librosa
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from scipy.fft import fft, fftfreq
from scipy.signal import correlate

# Funzione per ottenere il percorso relativo
def get_relative_path(*path_parts):
    return os.path.join(os.path.dirname(__file__), *path_parts)

# Step 1: Load the sound file
def load_sound(filename, to_mono=True):
    sound, sample_rate = sf.read(filename)
    if to_mono and sound.ndim > 1:  # Check if the sound is stereo
        sound = np.mean(sound, axis=1)  # Convert to mono by averaging the channels
    return sound, sample_rate

# Step 2: Remove silence
def remove_silence(audio, sample_rate, top_db=20):
    """
    Remove silence from the beginning and end of the audio
    """
    non_silent_intervals = librosa.effects.split(audio, top_db=top_db)
    non_silent_audio = np.concatenate([audio[start:end] for start,
                                        end in non_silent_intervals])
    return non_silent_audio

# Step 3: Adjust amplitude
def adjust_amplitude(signal, target_rms):
    """
    Adjust the amplitude of a signal to a target RMS
    """
    current_rms = np.sqrt(np.mean(signal**2))
    scaling_factor = target_rms / current_rms
    return signal * scaling_factor

# Step 4: Apply equalization
def equalize_audio(audio, sample_rate):
    """
    Apply equalization to the audio signal
    """
    # Example: Apply a simple high-pass filter
    nyquist = 0.5 * sample_rate
    low = 100 / nyquist
    b, a = butter(1, low, btype='high')
    equalized_audio = lfilter(b, a, audio)
    return equalized_audio

# Step 5: Calculate RMS
def calculate_rms(signal):
    return np.sqrt(np.mean(signal**2))

# Step 6: Apply fade-in and fade-out
def apply_crossfade(signal1, signal2, fade_duration, sample_rate, min_rms=0.1):
    """
    Apply a crossfade between two signals, reducing signal1 to min_rms
    """
    fade_samples = int(fade_duration * sample_rate)
    fade_in_curve = np.linspace(0, 1, fade_samples)
    fade_out_curve = np.linspace(1, min_rms, fade_samples)
    
    signal1[:fade_samples] *= fade_out_curve
    signal2[:fade_samples] *= fade_in_curve
    
    return signal1, signal2

# Step 7: Mix audio streams
def mix_audio_streams(word_sound, pink_noise, sample_rate, word_start_times,
                       max_duration=10, target_rms=0.02):
    # Adjust the amplitude of the pink noise to match the target RMS
    pink_noise = adjust_amplitude(pink_noise, target_rms + 0.005)  # Increment the target RMS slightly
    
    # Initialize the final audio stream with pink noise
    final_audio = pink_noise[:int(max_duration * sample_rate)].copy()
    
    # Calculate the RMS of the pink noise
    pink_noise_rms = calculate_rms(pink_noise)
    
    # Adjust the amplitude of the word sound to match the RMS of the pink noise
    word_sound_adjusted = adjust_amplitude(word_sound, pink_noise_rms)
    
    for start_time in word_start_times:
        # Calculate the start and end indices for the word sound
        start_idx = int(start_time * sample_rate)
        end_idx = start_idx + len(word_sound_adjusted)
        
        if end_idx > len(final_audio):
            break  # Ensure we do not exceed the maximum duration
        
        # Apply crossfade between pink noise and word sound
        pink_noise_segment = final_audio[start_idx:end_idx]
        word_sound_segment = word_sound_adjusted.copy()
        pink_noise_segment, word_sound_segment = apply_crossfade(pink_noise_segment,
                                                                  word_sound_segment,
                                                                  fade_duration=0.1,
                                                                  sample_rate=sample_rate,
                                                                  min_rms=0.1)
        
        # Overlay the word sound on the pink noise
        final_audio[start_idx:end_idx] = pink_noise_segment + word_sound_segment
    
    return final_audio

# Step 8: Play the sound using sounddevice
def play_audio(audio, sample_rate):
    sd.play(audio, samplerate=sample_rate)
    sd.wait()  # Wait until playback is finished

# Step 9: Extract features
def extract_features(audio, sample_rate):
    rms = librosa.feature.rms(y=audio)[0]
    envelope = np.abs(librosa.onset.onset_strength(y=audio, sr=sample_rate))
    zero_crossings = librosa.zero_crossings(audio, pad=False)
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
    
    return rms, envelope, zero_crossings, spectral_centroid

# Step 10: Plot features
def plot_features(audio, sample_rate, rms, envelope, zero_crossings,
                  spectral_centroid):
    times = np.arange(len(audio)) / float(sample_rate)
    
    plt.figure(figsize=(14, 8))
    
    plt.subplot(4, 1, 1)
    plt.plot(times, audio, label='Audio Signal')
    plt.title('Audio Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    
    plt.subplot(4, 1, 2)
    plt.plot(times[:len(rms)], rms, label='RMS')
    plt.title('Root Mean Square (RMS)')
    plt.xlabel('Time (s)')
    plt.ylabel('RMS')
    
    plt.subplot(4, 1, 3)
    plt.plot(times[:len(envelope)], envelope, label='Envelope')
    plt.title('Envelope')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    
    plt.subplot(4, 1, 4)
    plt.plot(times[:len(spectral_centroid)], spectral_centroid,
             label='Spectral Centroid')
    plt.title('Spectral Centroid')
    plt.xlabel('Time (s)')
    plt.ylabel('Hz')
    
    plt.tight_layout()
    plt.show()

# Funzione per calcolare lo spettro di frequenza
def plot_spectrum(audio, sample_rate):
    N = len(audio)
    yf = fft(audio)
    xf = fftfreq(N, 1 / sample_rate)[:N // 2]
    plt.plot(xf, 2.0 / N * np.abs(yf[:N // 2]))
    plt.title('Frequency Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.grid()
    plt.show()

# Funzione per calcolare il rapporto segnale-rumore (SNR)
def calculate_snr(signal, noise):
    signal_power = np.mean(signal**2)
    noise_power = np.mean(noise**2)
    snr = 10 * np.log10(signal_power / noise_power)
    return snr

# Example usage
sample_rate = 44100  # Standard sampling rate

# Set the default audio device to the first available device
# sd.default.device = 0

# Load the word sound
word_sound_path = get_relative_path('data', 'remedy_data', 'pwd',
                                     'pseudoparola_A.wav')
word_sound, word_sample_rate = load_sound(word_sound_path, to_mono=True)

# Remove silence from the word sound
word_sound = remove_silence(word_sound, word_sample_rate)

# Apply equalization to the word sound
word_sound = equalize_audio(word_sound, sample_rate)

# Load the pink noise
pink_noise_path = get_relative_path('pink_noise_20min.wav')
pink_noise, pink_noise_sample_rate = load_sound(pink_noise_path, to_mono=True)

# Apply equalization to the pink noise
pink_noise = equalize_audio(pink_noise, sample_rate)

# Define the start times for the word sound in seconds
word_start_times = [1, 3, 5, 7, 9]

# Create the mixed audio stream with a target RMS of 0.02
final_audio = mix_audio_streams(word_sound, pink_noise, sample_rate,
                                 word_start_times, max_duration=10, target_rms=0.02)

# Step 7: Play the final audio
play_audio(final_audio, sample_rate)

# # Step 8: Extract and plot features
# rms, envelope, zero_crossings, spectral_centroid = extract_features(final_audio,
#                                                                      sample_rate)
# plot_features(final_audio, sample_rate, rms, envelope, zero_crossings,
#                spectral_centroid)

# # Plot features of the word sound without pink noise
# rms_word, envelope_word, zero_crossings_word, spectral_centroid_word = extract_features(word_sound,
#                                                                                          sample_rate)
# plot_features(word_sound, sample_rate, rms_word, envelope_word, zero_crossings_word,
#                spectral_centroid_word)

# # Ensure the signals have the same length for SNR calculation
# min_length = min(len(word_sound), len(final_audio))
# word_sound = word_sound[:min_length]
# final_audio = final_audio[:min_length]

# # Plot dello spettro di frequenza
# plot_spectrum(final_audio, sample_rate)

# # Calcolo del SNR solo durante i periodi in cui la pseudoparola è presente
# snr_values = []
# for start_time in word_start_times:
#     start_idx = int(start_time * sample_rate)
#     end_idx = start_idx + len(word_sound)
#     if end_idx > len(final_audio):
#         break
#     snr = calculate_snr(word_sound, final_audio[start_idx:end_idx] - word_sound)
#     snr_values.append(snr)
#     print(f'SNR at {start_time}s: {snr} dB')

# # Calcolo della cross-correlazione
# correlation = correlate(final_audio, word_sound, mode='full')
# plt.plot(correlation)
# plt.title('Cross-Correlation')
# plt.xlabel('Lag')
# plt.ylabel('Correlation')
# plt.grid()
# plt.show()
