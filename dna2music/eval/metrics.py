import numpy as np
import pandas as pd
from collections import Counter
from scipy.stats import pearsonr
from sklearn.metrics.pairwise import cosine_similarity

def pitch_class_histogram_entropy(notes):
    """Calculate pitch-class histogram entropy"""
    if not notes:
        return 0.0
    
    # Extract pitch classes (0-11)
    pitch_classes = [note['pitch'] % 12 for note in notes]
    
    # Count occurrences
    pc_counts = Counter(pitch_classes)
    total_notes = len(pitch_classes)
    
    # Calculate entropy
    entropy = 0.0
    for count in pc_counts.values():
        p = count / total_notes
        if p > 0:
            entropy -= p * np.log2(p)
    
    return entropy

def n_gram_novelty(notes, training_notes, n=3):
    """Calculate n-gram novelty compared to training set"""
    if not notes or not training_notes:
        return 0.0
    
    # Extract n-grams from generated notes
    generated_ngrams = []
    for i in range(len(notes) - n + 1):
        ngram = tuple(notes[j]['pitch'] for j in range(i, i + n))
        generated_ngrams.append(ngram)
    
    # Extract n-grams from training notes
    training_ngrams = []
    for i in range(len(training_notes) - n + 1):
        ngram = tuple(training_notes[j]['pitch'] for j in range(i, i + n))
        training_ngrams.append(ngram)
    
    # Calculate novelty
    generated_set = set(generated_ngrams)
    training_set = set(training_ngrams)
    
    novel_ngrams = generated_set - training_set
    novelty = len(novel_ngrams) / len(generated_set) if generated_set else 0.0
    
    return novelty

def gc_content_rhythm_correlation(dna_seq, notes):
    """Calculate correlation between GC content and rhythm"""
    if not dna_seq or not notes:
        return 0.0
    
    # Calculate GC content for DNA windows
    window_size = 100
    gc_contents = []
    for i in range(0, len(dna_seq) - window_size + 1, window_size):
        window = dna_seq[i:i + window_size]
        gc_count = window.count('G') + window.count('C')
        gc_content = gc_count / len(window)
        gc_contents.append(gc_content)
    
    # Calculate rhythm density (notes per time unit)
    if len(notes) < 2:
        return 0.0
    
    rhythm_density = []
    time_window = 1.0  # 1 second windows
    current_time = 0.0
    notes_in_window = 0
    
    for note in notes:
        if note['start'] >= current_time + time_window:
            rhythm_density.append(notes_in_window)
            current_time += time_window
            notes_in_window = 1
        else:
            notes_in_window += 1
    
    # Add final window
    if notes_in_window > 0:
        rhythm_density.append(notes_in_window)
    
    # Ensure same length
    min_len = min(len(gc_contents), len(rhythm_density))
    if min_len < 2:
        return 0.0
    
    gc_contents = gc_contents[:min_len]
    rhythm_density = rhythm_density[:min_len]
    
    # Calculate Pearson correlation
    correlation, p_value = pearsonr(gc_contents, rhythm_density)
    
    return correlation

def musical_coherence(notes):
    """Calculate musical coherence score"""
    if len(notes) < 2:
        return 0.0
    
    # Extract features
    pitches = [note['pitch'] for note in notes]
    velocities = [note['velocity'] for note in notes]
    durations = [note['duration'] for note in notes]
    
    # Pitch coherence (smoothness)
    pitch_changes = np.diff(pitches)
    pitch_coherence = 1.0 / (1.0 + np.std(pitch_changes))
    
    # Velocity coherence
    velocity_coherence = 1.0 / (1.0 + np.std(velocities))
    
    # Duration coherence
    duration_coherence = 1.0 / (1.0 + np.std(durations))
    
    # Overall coherence
    coherence = (pitch_coherence + velocity_coherence + duration_coherence) / 3.0
    
    return coherence

def evaluate_dna_music(dna_seq, notes, training_notes=None):
    """Comprehensive evaluation of DNA-to-music conversion"""
    results = {}
    
    # Basic metrics
    results['note_count'] = len(notes)
    results['sequence_length'] = len(dna_seq)
    
    # Musical metrics
    results['pitch_entropy'] = pitch_class_histogram_entropy(notes)
    results['musical_coherence'] = musical_coherence(notes)
    
    # Novelty (if training data available)
    if training_notes:
        results['novelty_3gram'] = n_gram_novelty(notes, training_notes, n=3)
        results['novelty_5gram'] = n_gram_novelty(notes, training_notes, n=5)
    
    # DNA-music correlation
    results['gc_rhythm_correlation'] = gc_content_rhythm_correlation(dna_seq, notes)
    
    # Pitch range
    if notes:
        pitches = [note['pitch'] for note in notes]
        results['pitch_range'] = max(pitches) - min(pitches)
        results['avg_pitch'] = np.mean(pitches)
        results['pitch_std'] = np.std(pitches)
    
    return results

def generate_evaluation_report(results_list, output_file='evaluation_report.json'):
    """Generate comprehensive evaluation report"""
    if not results_list:
        return
    
    # Aggregate results
    report = {
        'summary': {
            'total_sequences': len(results_list),
            'avg_note_count': np.mean([r['note_count'] for r in results_list]),
            'avg_pitch_entropy': np.mean([r['pitch_entropy'] for r in results_list]),
            'avg_musical_coherence': np.mean([r['musical_coherence'] for r in results_list]),
            'avg_gc_correlation': np.mean([r['gc_rhythm_correlation'] for r in results_list])
        },
        'detailed_results': results_list
    }
    
    # Save report
    import json
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report 