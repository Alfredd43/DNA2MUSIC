import pytest
from hypothesis import given, strategies as st
from dna2music.mapping import parser, composer

def test_parse_raw():
    seq = parser.parse_raw(['ACGTacgtNNN'])
    assert seq == 'ACGTACGT'

def test_parse_fasta():
    fasta = ['>seq1', 'ACGT', 'TGCA']
    seq = parser.parse_fasta(fasta)
    assert seq == 'ACGTTGCA'

def test_codons():
    seq = 'ACGTGCAAA'
    cods = composer.codons(seq)
    assert cods == ['ACG', 'TGC', 'AAA']

@given(st.text(alphabet='ACGT', min_size=100, max_size=200))
def test_sliding_features(seq):
    df = parser.sliding_features(seq, window=50, step=10)
    assert not df.empty
    assert all(0 <= gc <= 1 for gc in df.gc)
    assert all(0 <= ent <= 2 for ent in df.entropy) 