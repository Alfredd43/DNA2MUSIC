import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import os
import json
from dna2music.models.lstm_melody import LSTMMelody, encode_abc_style
from dna2music.mapping import parser, composer

class MelodyDataset(Dataset):
    def __init__(self, data_dir, seq_length=64):
        self.seq_length = seq_length
        self.data = []
        self.vocab = {}
        self.vocab_size = 0
        
        # Load ABC files or generate from DNA
        for file in os.listdir(data_dir):
            if file.endswith('.abc'):
                with open(os.path.join(data_dir, file)) as f:
                    self.data.extend(self.tokenize(f.read()))
        
        # Build vocabulary
        all_tokens = set()
        for seq in self.data:
            all_tokens.update(seq)
        self.vocab = {token: i for i, token in enumerate(all_tokens)}
        self.vocab_size = len(self.vocab)
    
    def tokenize(self, text):
        # Simple tokenization for ABC format
        return text.split()
    
    def __len__(self):
        return len(self.data) - self.seq_length
    
    def __getitem__(self, idx):
        seq = self.data[idx:idx + self.seq_length]
        target = self.data[idx + 1:idx + self.seq_length + 1]
        
        # Convert to indices
        x = torch.tensor([self.vocab.get(token, 0) for token in seq], dtype=torch.long)
        y = torch.tensor([self.vocab.get(token, 0) for token in target], dtype=torch.long)
        
        return x, y

def train_lstm(args):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Load dataset
    dataset = MelodyDataset(args.dataset_dir, seq_length=args.seq_length)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    
    # Initialize model
    model = LSTMMelody(
        vocab_size=dataset.vocab_size,
        embedding_dim=args.embedding_dim,
        lstm_units=args.lstm_units,
        num_layers=args.num_layers,
        dropout=args.dropout
    ).to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)
    
    # Training loop
    for epoch in range(args.epochs):
        model.train()
        total_loss = 0
        
        for batch_idx, (x, y) in enumerate(dataloader):
            x, y = x.to(device), y.to(device)
            
            optimizer.zero_grad()
            output, _ = model(x)
            
            # Reshape for loss calculation
            output = output.view(-1, dataset.vocab_size)
            y = y.view(-1)
            
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
            if batch_idx % 100 == 0:
                print(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}')
        
        avg_loss = total_loss / len(dataloader)
        print(f'Epoch {epoch} completed. Average loss: {avg_loss:.4f}')
        
        # Save checkpoint
        if (epoch + 1) % args.save_every == 0:
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'vocab': dataset.vocab,
                'vocab_size': dataset.vocab_size,
                'args': vars(args)
            }
            torch.save(checkpoint, os.path.join(args.save_dir, f'checkpoint_epoch_{epoch}.pt'))
    
    # Save final model
    torch.save(model.state_dict(), os.path.join(args.save_dir, 'final_model.pt'))
    print(f'Training completed. Model saved to {args.save_dir}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_dir', default='data/chorales_abc', help='Directory with ABC files')
    parser.add_argument('--vocab_size', type=int, default=128, help='Vocabulary size')
    parser.add_argument('--embedding_dim', type=int, default=64, help='Embedding dimension')
    parser.add_argument('--lstm_units', type=int, default=256, help='LSTM hidden units')
    parser.add_argument('--num_layers', type=int, default=2, help='Number of LSTM layers')
    parser.add_argument('--dropout', type=float, default=0.2, help='Dropout rate')
    parser.add_argument('--seq_length', type=int, default=64, help='Sequence length')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--learning_rate', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--save_every', type=int, default=10, help='Save every N epochs')
    parser.add_argument('--save_dir', default='checkpoints/lstm', help='Save directory')
    
    args = parser.parse_args()
    
    # Create save directory
    os.makedirs(args.save_dir, exist_ok=True)
    
    train_lstm(args) 