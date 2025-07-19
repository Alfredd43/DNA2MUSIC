import torch
import torch.nn as nn
import torch.nn.functional as F

class LSTMMelody(nn.Module):
    def __init__(self, vocab_size=128, embedding_dim=64, lstm_units=256, num_layers=2, dropout=0.2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, lstm_units, num_layers, dropout=dropout, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(lstm_units, vocab_size)
        
    def forward(self, x, hidden=None):
        embedded = self.embedding(x)
        lstm_out, hidden = self.lstm(embedded, hidden)
        lstm_out = self.dropout(lstm_out)
        output = self.fc(lstm_out)
        return output, hidden
    
    def init_hidden(self, batch_size, device):
        return (torch.zeros(2, batch_size, 256).to(device),
                torch.zeros(2, batch_size, 256).to(device))

def encode_abc_style(notes):
    """Convert note events to ABC-like string encoding"""
    # Simple encoding: "A60 C64 E67 ..." (note + pitch)
    encoded = []
    for note in notes:
        pitch = note.get('pitch', 60)
        duration = note.get('duration', 1.0)
        encoded.append(f"{chr(65 + (pitch % 12))}{pitch}")
    return ' '.join(encoded)

def decode_abc_style(encoded):
    """Convert ABC-like string back to note events"""
    notes = []
    parts = encoded.split()
    for part in parts:
        if len(part) >= 2:
            note = part[0]
            pitch = int(part[1:])
            notes.append({'pitch': pitch, 'duration': 1.0, 'velocity': 100})
    return notes 