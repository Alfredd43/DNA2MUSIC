import argparse
import os
import numpy as np
import tensorflow as tf
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel
from dna2music.mapping import parser, composer

def reverse_complement(seq):
    """DNA reverse complement ↔ retrograde melody"""
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    return ''.join(complement[base] for base in reversed(seq))

def snp_mutation(seq, mutation_rate=0.01):
    """Random SNP mutation ↔ pitch jitter ±1 semitone"""
    bases = ['A', 'C', 'G', 'T']
    mutated = list(seq)
    for i in range(len(mutated)):
        if np.random.random() < mutation_rate:
            mutated[i] = np.random.choice(bases)
    return ''.join(mutated)

def augment_dna_sequence(seq, augmentations=['reverse_complement', 'snp_mutation']):
    """Apply DNA-specific augmentations"""
    augmented = [seq]
    
    if 'reverse_complement' in augmentations:
        augmented.append(reverse_complement(seq))
    
    if 'snp_mutation' in augmentations:
        for _ in range(3):  # Generate 3 mutations
            augmented.append(snp_mutation(seq))
    
    return augmented

def dna_to_melody_sequence(seq, config):
    """Convert DNA to melody sequence for MusicVAE"""
    # Parse DNA and get features
    features = parser.sliding_features(seq, window=100, step=10)
    
    # Generate chords from DNA
    chords = composer.compose_chords(seq)
    
    # Convert to melody sequence (simplified)
    melody = []
    for i, chord in enumerate(chords):
        # Take first note of each chord as melody
        melody.append(chord[0] if chord else 60)
    
    # Pad/truncate to config max_seq_len
    max_len = config.hparams.max_seq_len
    if len(melody) > max_len:
        melody = melody[:max_len]
    else:
        melody.extend([0] * (max_len - len(melody)))
    
    return np.array(melody)

def train_musicvae(args):
    # Load MusicVAE config
    config = configs.CONFIG_MAP[args.config_name]
    
    # Initialize model
    model = TrainedModel(config, batch_size=args.batch_size, checkpoint_dir_or_path=args.checkpoint_dir)
    
    # Load training data
    training_data = []
    
    # Generate training data from DNA sequences
    if args.dna_data_dir:
        for file in os.listdir(args.dna_data_dir):
            if file.endswith(('.fasta', '.txt')):
                with open(os.path.join(args.dna_data_dir, file)) as f:
                    seq = parser.parse_dna(f)
                    
                    # Apply augmentations
                    augmented_seqs = augment_dna_sequence(seq, args.augmentations)
                    
                    for aug_seq in augmented_seqs:
                        melody = dna_to_melody_sequence(aug_seq, config)
                        training_data.append(melody)
    
    # Convert to tensor
    training_data = np.array(training_data)
    
    # Training loop (simplified - MusicVAE training is complex)
    print(f"Loaded {len(training_data)} training sequences")
    print(f"Training MusicVAE with config: {args.config_name}")
    print(f"Augmentations: {args.augmentations}")
    
    # Save training data for later use
    np.save(os.path.join(args.save_dir, 'training_data.npy'), training_data)
    
    # Note: Full MusicVAE training requires significant infrastructure
    # This is a simplified version - in practice you'd use their training scripts
    print("Training data prepared. Use magenta's training scripts for full training.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_name', default='mel_4bar_small_q2', help='MusicVAE config name')
    parser.add_argument('--checkpoint_dir', default='checkpoints/musicvae', help='Checkpoint directory')
    parser.add_argument('--dna_data_dir', default='data/dna_sequences', help='Directory with DNA files')
    parser.add_argument('--augmentations', nargs='+', default=['reverse_complement', 'snp_mutation'], 
                       help='Augmentation methods')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--save_dir', default='checkpoints/musicvae', help='Save directory')
    
    args = parser.parse_args()
    
    # Create save directory
    os.makedirs(args.save_dir, exist_ok=True)
    
    train_musicvae(args) 