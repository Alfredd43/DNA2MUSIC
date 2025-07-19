import os
import numpy as np
import soundfile as sf
from dna2music.mapping import parser, composer

def process_dna_task(job_id, file_content, jobs):
    try:
        # Parse DNA
        seq = parser.parse_dna(file_content.decode())
        # Generate features
        features = parser.sliding_features(seq, window=100, step=10)
        # Compose chords
        chords = composer.compose_chords(seq)
        # Convert to note events
        notes = composer.to_note_events(chords)
        # Generate audio
        sample_rate = 44100
        duration = 0.1  # seconds per note
        audio_samples = []
        for note in notes:
            frequency = 440 * (2 ** ((note['pitch'] - 69) / 12))  # A4 = 440Hz
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.sin(2 * np.pi * frequency * t)
            wave *= note['velocity'] / 127.0
            audio_samples.append(wave)
        audio = np.concatenate(audio_samples)
        audio = audio / np.max(np.abs(audio))
        output_path = f"outputs/{job_id}.wav"
        os.makedirs("outputs", exist_ok=True)
        sf.write(output_path, audio, sample_rate)
        # Update job status
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = {
            "audio_path": f"/files/{job_id}.wav",
            "note_count": len(notes),
            "sequence_length": len(seq),
            "notes": notes[:50]
        }
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e) 