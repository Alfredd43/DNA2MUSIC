import pandas as pd
import numpy as np
from numba import njit
import re

@njit
def gc_content(seq):
    gc = 0
    for c in seq:
        if c == 'G' or c == 'C':
            gc += 1
    return gc / len(seq) if len(seq) > 0 else 0

@njit
def shannon_entropy(seq):
    bases = ['A', 'C', 'G', 'T']
    counts = np.array([seq.count(b) for b in bases])
    probs = counts / counts.sum() if counts.sum() > 0 else np.zeros(4)
    entropy = 0.0
    for p in probs:
        if p > 0:
            entropy -= p * np.log2(p)
    return entropy

def parse_fasta(f):
    seq = ''
    for line in f:
        if line.startswith('>'):
            continue
        seq += line.strip().upper()
    return seq

def parse_fastq(f):
    seq = ''
    for i, line in enumerate(f):
        if i % 4 == 1:
            seq += line.strip().upper()
    return seq

def parse_23andme(f):
    seq = ''
    for line in f:
        if line.startswith('#') or line.strip() == '':
            continue
        parts = line.strip().split('\t')
        if len(parts) >= 4:
            base = parts[3].upper()
            if base in 'ACGT':
                seq += base
    return seq

def parse_raw(f):
    return ''.join([re.sub(r'[^ACGT]', '', line.upper()) for line in f])

def parse_dna(file, fmt='auto'):
    if hasattr(file, 'read'):
        lines = file.read().decode().splitlines()
    elif isinstance(file, str):
        lines = file.splitlines()
    else:
        lines = list(file)
    if fmt == 'auto':
        if any(l.startswith('>') for l in lines):
            fmt = 'fasta'
        elif any(l.startswith('@') for l in lines):
            fmt = 'fastq'
        elif any('23andMe' in l for l in lines):
            fmt = '23andme'
        else:
            fmt = 'raw'
    if fmt == 'fasta':
        seq = parse_fasta(lines)
    elif fmt == 'fastq':
        seq = parse_fastq(lines)
    elif fmt == '23andme':
        seq = parse_23andme(lines)
    else:
        seq = parse_raw(lines)
    return seq

def sliding_features(seq, window=100, step=10):
    data = []
    for i in range(0, len(seq) - window + 1, step):
        w = seq[i:i+window]
        gc = gc_content(w)
        ent = shannon_entropy(w)
        data.append({'start': i, 'end': i+window, 'gc': gc, 'entropy': ent, 'seq': w})
    return pd.DataFrame(data) 