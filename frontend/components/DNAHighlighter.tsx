import React from 'react';

interface DNAHighlighterProps {
  sequence: string;
  currentIndex: number;
  windowSize?: number;
}

export default function DNAHighlighter({ sequence, currentIndex, windowSize = 3 }: DNAHighlighterProps) {
  return (
    <div className="dna-sequence text-lg font-mono break-all p-2 bg-background-800 rounded-lg mb-4">
      {sequence.split('').map((base, i) => (
        <span
          key={i}
          style={{
            background: i >= currentIndex && i < currentIndex + windowSize ? '#4ade80' : 'transparent',
            color: i >= currentIndex && i < currentIndex + windowSize ? '#101014' : undefined,
            fontWeight: i >= currentIndex && i < currentIndex + windowSize ? 'bold' : undefined,
            transition: 'background 0.2s',
            borderRadius: '2px',
            padding: '0 1px',
          }}
        >
          {base}
        </span>
      ))}
    </div>
  );
} 