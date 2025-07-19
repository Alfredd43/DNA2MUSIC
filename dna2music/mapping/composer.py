import numpy as np
import itertools

# 64 codons
CODONS = [''.join(c) for c in itertools.product('ACGT', repeat=3)]

# Precompute a simple 3-voice chord table (root, third, fifth)
BASE_PITCH = 48  # C3
CHORD_TABLE = {c: [BASE_PITCH + i*4 + j for j in (0, 4, 7)] for i, c in enumerate(CODONS)}

# Pentatonic scale mask (C major pentatonic: C D E G A)
PENTATONIC_MASK = [0, 2, 4, 7, 9]
MAJOR_MASK = [0, 2, 4, 5, 7, 9, 11]

# Markov rhythm prior (stub)
def markov_rhythm_prior(seq_len):
    # TODO: Learn from Bach chorales
    return np.ones(seq_len) / seq_len

def codons(seq):
    return [seq[i:i+3] for i in range(0, len(seq)-2, 3)]

def scale_mask_pitch(pitch, mask, base=60):
    # Snap pitch to nearest note in the scale mask
    rel = (pitch - base) % 12
    closest = min(mask, key=lambda x: abs(x - rel))
    return base + ((pitch - base) // 12) * 12 + closest

def compose_chords(seq):
    return [CHORD_TABLE.get(c, [60, 64, 67]) for c in codons(seq)]

def to_note_events(chords, durations=None, velocities=None, beautiful_melody=False, scale_mask=None):
    events = []
    last_pitch = None
    mask = scale_mask if scale_mask is not None else PENTATONIC_MASK if beautiful_melody else None
    for i, chord in enumerate(chords):
        for note in chord:
            pitch = note
            # Beautiful mode: snap to scale, limit jumps
            if beautiful_melody and mask:
                pitch = scale_mask_pitch(pitch, mask)
                if last_pitch is not None and abs(pitch - last_pitch) > 7:
                    # Limit big jumps
                    pitch = last_pitch + np.sign(pitch - last_pitch) * 5
            last_pitch = pitch
            # Beautiful mode: add rhythm
            duration = durations[i] if durations else (0.5 if beautiful_melody and i % 2 == 0 else 1.0)
            velocity = velocities[i] if velocities else (100 if not beautiful_melody else (90 + 20 * (i % 2)))
            events.append({'pitch': pitch, 'start': i, 'duration': duration, 'velocity': velocity})
    return events

# LSTM smoothing (optional, free, if model available)
def smooth_melody_with_lstm(notes, lstm_model=None):
    # If no model, just return notes
    if lstm_model is None:
        return notes
    # TODO: Implement LSTM-based smoothing/generation
    # For now, just return notes
    return notes 