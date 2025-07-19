import os
import numpy as np
import soundfile as sf
from dna2music.mapping import parser, composer
from dna2music.utils.audio import generate_audio_simple
import json

def process_dna_task(job_id, file_content, redis_client):
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
        # Generate audio
        audio_path = generate_audio_simple(notes, job_id)
        # Update job status in Redis
        redis_client.hset(f"job:{job_id}", mapping={
            "status": "completed",
            "result": json.dumps({
                "audio_path": f"/files/{job_id}.wav",
                "note_count": len(notes),
                "sequence_length": len(seq),
                "notes": notes[:50]
            }),
            "error": ""
        })
    except UnicodeDecodeError:
        redis_client.hset(f"job:{job_id}", mapping={
            "status": "failed",
            "error": "File could not be decoded. Please upload a valid text file."
        })
    except Exception as e:
        redis_client.hset(f"job:{job_id}", mapping={
            "status": "failed",
            "error": f"Processing error: {str(e)}"
        }) 