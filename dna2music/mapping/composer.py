import numpy as np
import itertools
import json
import os

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'configs', 'default.json')
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

SCALES = CONFIG.get('scales', {})
RHYTHM_RULES = CONFIG.get('rhythm_rules', {})
MOTIFS = CONFIG.get('motifs', {})

# 64 codons
CODONS = [''.join(c) for c in itertools.product('ACGT', repeat=3)]

# Precompute a simple 3-voice chord table (root, third, fifth)
BASE_PITCH = 48  # C3
CHORD_TABLE = {c: [BASE_PITCH + i*4 + j for j in (0, 4, 7)] for i, c in enumerate(CODONS)}

# Default scale masks
PENTATONIC_MASK = SCALES.get('pentatonic', [0, 2, 4, 7, 9])
MAJOR_MASK = SCALES.get('major', [0, 2, 4, 5, 7, 9, 11])
BLUES_MASK = SCALES.get('blues', [0, 3, 5, 6, 7, 10])
CINEMATIC_MASK = SCALES.get('cinematic', [0, 2, 3, 6, 7, 11])
MINOR_MASK = SCALES.get('minor', [0, 2, 3, 5, 7, 8, 10])

# Markov rhythm prior (stub)
def markov_rhythm_prior(seq_len):
    return np.ones(seq_len) / seq_len

def codons(seq):
    return [seq[i:i+3] for i in range(0, len(seq)-2, 3)]

def scale_mask_pitch(pitch, mask, base=60):
    rel = (pitch - base) % 12
    closest = min(mask, key=lambda x: abs(x - rel))
    return base + ((pitch - base) // 12) * 12 + closest

def select_scale(gc):
    if gc < 0.4:
        return MAJOR_MASK
    elif gc < 0.6:
        return PENTATONIC_MASK
    elif gc < 0.7:
        return BLUES_MASK
    else:
        return CINEMATIC_MASK

def find_motifs(seq, motifs):
    found = []
    for motif, phrase in motifs.items():
        idx = seq.find(motif)
        if idx != -1:
            found.append((idx, phrase))
    return found

def compose_chords(seq):
    # Motif-to-phrase mapping (stub: just mark motif positions)
    motifs_found = find_motifs(seq, MOTIFS)
    chords = [CHORD_TABLE.get(c, [60, 64, 67]) for c in codons(seq)]
    # Optionally, insert special chords/phrases at motif positions
    # (left as an exercise for further expansion)
    return chords

def get_note_duration(gc, entropy, rules):
    # Use GC content for rhythm
    if gc < 0.4:
        return rules['gc_content']['low']
    elif gc < 0.6:
        return rules['gc_content']['medium']
    else:
        return rules['gc_content']['high']

def to_note_events(
    chords,
    gc_seq=None,
    entropy_seq=None,
    velocities=None,
    mode='beautiful',
    scale_mask=None,
    rhythm_rules=None
):
    events = []
    last_pitch = None
    # Choose mask based on mode
    mode_map = {
        'beautiful': PENTATONIC_MASK,
        'major': MAJOR_MASK,
        'blues': BLUES_MASK,
        'cinematic': CINEMATIC_MASK,
        'minor': MINOR_MASK
    }
    mask = scale_mask if scale_mask is not None else mode_map.get(mode, PENTATONIC_MASK)
    for i, chord in enumerate(chords):
        # Dynamic scale selection
        if gc_seq is not None:
            mask = select_scale(gc_seq[i])
        for note in chord:
            pitch = note
            if mask:
                pitch = scale_mask_pitch(pitch, mask)
            # Dynamic rhythm
            duration = 1.0
            if gc_seq is not None and entropy_seq is not None and rhythm_rules is not None:
                duration = get_note_duration(gc_seq[i], entropy_seq[i], rhythm_rules)
            velocity = velocities[i] if velocities else 100
            events.append({'pitch': pitch, 'start': i, 'duration': duration, 'velocity': velocity})
            last_pitch = pitch
    return events

# LSTM smoothing (optional, free, if model available)
def smooth_melody_with_lstm(notes, lstm_model=None):
    if lstm_model is None:
        return notes
    return notes 