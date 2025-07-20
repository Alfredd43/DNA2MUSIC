import os
import json
import numpy as np
from celery import Celery
from dna2music.mapping import parser, composer
from dna2music.models.lstm_melody import LSTMMelody, encode_abc_style, decode_abc_style
import torch
from dna2music.utils.audio import generate_audio_simple

# Initialize Celery
celery_app = Celery('dna2music')
celery_app.config_from_object('celeryconfig')

def enhance_with_lstm(notes):
    model_path = "dna2music/models/checkpoints/lstm/final_model.pt"
    if not os.path.exists(model_path):
        return notes  # fallback
    model = LSTMMelody(vocab_size=128, embedding_dim=64, lstm_units=256)
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    # Convert notes to ABC-like encoding
    abc_encoded = encode_abc_style(notes)
    # Tokenize: convert ABC string to integer indices (simple mapping: pitch only)
    tokens = [int(tok[1:]) for tok in abc_encoded.split()]
    input_tensor = torch.tensor(tokens, dtype=torch.long).unsqueeze(0)  # shape (1, seq_len)
    with torch.no_grad():
        output, _ = model(input_tensor)
        # Get predicted pitches (argmax over vocab)
        pred_indices = output.argmax(dim=-1).squeeze(0).tolist()
    # Decode back to note events
    enhanced_notes = []
    for idx, orig_note in enumerate(notes):
        pitch = pred_indices[idx] if idx < len(pred_indices) else orig_note.get('pitch', 60)
        enhanced_notes.append({
            'pitch': pitch,
            'duration': orig_note.get('duration', 1.0),
            'velocity': orig_note.get('velocity', 100)
        })
    return enhanced_notes

def enhance_with_musicvae(notes):
    # Stub for MusicVAE integration
    # Load trained MusicVAE model and use it to generate/enhance notes
    # For now, just return notes
    return notes

@celery_app.task
def process_dna_task(job_id: str, file_content: bytes):
    """Main DNA processing task"""
    try:
        # Parse DNA
        seq = parser.parse_dna(file_content.decode())
        # Generate features
        features = parser.sliding_features(seq, window=100, step=10)
        gc_seq = features['gc'].tolist() if 'gc' in features else None
        entropy_seq = features['entropy'].tolist() if 'entropy' in features else None
        # Compose chords
        chords = composer.compose_chords(seq)
        # Convert to note events with dynamic mapping
        from dna2music.mapping.composer import RHYTHM_RULES
        notes = composer.to_note_events(
            chords,
            gc_seq=gc_seq,
            entropy_seq=entropy_seq,
            mode='beautiful',
            rhythm_rules=RHYTHM_RULES
        )
        # LSTM enhancement
        enhanced_notes = enhance_with_lstm(notes)
        # MusicVAE enhancement (stub)
        final_notes = enhance_with_musicvae(enhanced_notes)
        # Generate audio (shared util)
        audio_path = generate_audio_simple(final_notes, job_id)
        # Update job status
        update_job_status(job_id, "completed", {
            "audio_path": audio_path,
            "note_count": len(final_notes),
            "sequence_length": len(seq)
        })
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        update_job_status(job_id, "failed", {"error": str(e)})
        raise

def update_job_status(job_id: str, status: str, result: dict):
    """Update job status (in production, use Redis/DB)"""
    # This would update the job status in Redis or database
    # For now, just print
    print(f"Job {job_id}: {status} - {result}")

if __name__ == '__main__':
    celery_app.start() 