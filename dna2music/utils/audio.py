import numpy as np
import soundfile as sf
import os

def generate_audio_simple(notes, job_id, output_dir="outputs"):
    sample_rate = 44100
    duration = 0.1  # seconds per note
    audio_samples = []
    for note in notes:
        frequency = 440 * (2 ** ((note['pitch'] - 69) / 12))
        t = np.linspace(0, duration, int(sample_rate * duration))
        wave = np.sin(2 * np.pi * frequency * t)
        wave *= note['velocity'] / 127.0
        audio_samples.append(wave)
    audio = np.concatenate(audio_samples)
    audio = audio / np.max(np.abs(audio))
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{job_id}.wav"
    sf.write(output_path, audio, sample_rate)
    return output_path 