import os
import json
import numpy as np
from celery import Celery
from dna2music.mapping import parser, composer
from dna2music.models.lstm_melody import LSTMMelody, encode_abc_style
import torch
import soundfile as sf
import librosa

# Initialize Celery
celery_app = Celery('dna2music')
celery_app.config_from_object('celeryconfig')

@celery_app.task
def process_dna_task(job_id: str, file_content: bytes):
    """Main DNA processing task"""
    try:
        # Parse DNA
        seq = parser.parse_dna(file_content.decode())
        
        # Generate features
        features = parser.sliding_features(seq, window=100, step=10)
        
        # Compose chords
        chords = composer.compose_chords(seq)
        
        # Convert to note events
        notes = composer.to_note_events(chords)
        
        # AI enhancement (simplified)
        enhanced_notes = enhance_with_ai(notes)
        
        # Generate audio
        audio_path = generate_audio(enhanced_notes, job_id)
        
        # Update job status
        update_job_status(job_id, "completed", {
            "audio_path": audio_path,
            "note_count": len(enhanced_notes),
            "sequence_length": len(seq)
        })
        
        return {"status": "success", "job_id": job_id}
        
    except Exception as e:
        update_job_status(job_id, "failed", {"error": str(e)})
        raise

def enhance_with_ai(notes):
    """Enhance notes with AI models"""
    # Load LSTM model if available
    try:
        model = load_lstm_model()
        enhanced = apply_lstm_enhancement(notes, model)
        return enhanced
    except:
        # Fallback to basic enhancement
        return apply_basic_enhancement(notes)

def load_lstm_model():
    """Load trained LSTM model"""
    model_path = "dna2music/models/checkpoints/lstm/final_model.pt"
    if os.path.exists(model_path):
        model = LSTMMelody(vocab_size=128, embedding_dim=64, lstm_units=256)
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
        model.eval()
        return model
    return None

def apply_lstm_enhancement(notes, model):
    """Apply LSTM enhancement to notes"""
    # Convert notes to ABC format
    abc_encoded = encode_abc_style(notes)
    
    # Generate enhanced sequence
    with torch.no_grad():
        # Simplified generation
        enhanced_notes = notes.copy()
        for i in range(len(enhanced_notes)):
            # Add some variation
            enhanced_notes[i]['pitch'] += np.random.randint(-2, 3)
            enhanced_notes[i]['velocity'] = min(127, max(0, enhanced_notes[i]['velocity'] + np.random.randint(-10, 11)))
    
    return enhanced_notes

def apply_basic_enhancement(notes):
    """Apply basic musical enhancement"""
    enhanced = []
    for i, note in enumerate(notes):
        # Add some musical variation
        enhanced_note = note.copy()
        
        # Slight pitch variation
        enhanced_note['pitch'] += np.random.randint(-1, 2)
        
        # Velocity variation based on position
        if i % 4 == 0:  # Downbeat
            enhanced_note['velocity'] = min(127, enhanced_note['velocity'] + 10)
        else:
            enhanced_note['velocity'] = max(0, enhanced_note['velocity'] - 5)
        
        enhanced.append(enhanced_note)
    
    return enhanced

def generate_audio(notes, job_id):
    """Generate WAV audio from notes"""
    # Convert notes to audio
    sample_rate = 44100
    duration = 0.1  # seconds per note
    
    # Generate audio samples
    audio_samples = []
    for note in notes:
        # Generate sine wave for each note
        frequency = 440 * (2 ** ((note['pitch'] - 69) / 12))  # A4 = 440Hz
        t = np.linspace(0, duration, int(sample_rate * duration))
        wave = np.sin(2 * np.pi * frequency * t)
        
        # Apply velocity (volume)
        wave *= note['velocity'] / 127.0
        
        audio_samples.append(wave)
    
    # Concatenate all samples
    audio = np.concatenate(audio_samples)
    
    # Normalize
    audio = audio / np.max(np.abs(audio))
    
    # Save to file
    output_path = f"outputs/{job_id}.wav"
    os.makedirs("outputs", exist_ok=True)
    sf.write(output_path, audio, sample_rate)
    
    return output_path

def update_job_status(job_id: str, status: str, result: dict):
    """Update job status (in production, use Redis/DB)"""
    # This would update the job status in Redis or database
    # For now, just print
    print(f"Job {job_id}: {status} - {result}")

if __name__ == '__main__':
    celery_app.start() 