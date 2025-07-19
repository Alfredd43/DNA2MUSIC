import { useCallback, useRef, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Play, Pause, Download, Music, Dna } from 'lucide-react';
import axios from 'axios';
import PianoRoll from '../components/PianoRoll';
import AudioPlayer from '../components/AudioPlayer';
import Hero from '../components/Hero';
import DNAHighlighter from '../components/DNAHighlighter';
import { useAppStore } from '../store/useAppStore';
import { Midi } from '@tonejs/midi';

export default function Home() {
  const {
    jobId, status, progress, result, error, beautifulMode,
    setJobId, setStatus, setProgress, setResult, setError, setBeautifulMode
  } = useAppStore();
  const [currentNoteIdx, setCurrentNoteIdx] = useState(0);
  const [dnaSeq, setDnaSeq] = useState('');
  const [sheetSvg, setSheetSvg] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;
    setStatus('uploading');
    setError(null);
    setProgress(0);
    try {
      const text = await file.text();
      setDnaSeq(text.replace(/[^ACGTacgt]/g, ''));
      const formData = new FormData();
      formData.append('file', file);
      formData.append('beautiful', beautifulMode ? '1' : '0');
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await axios.post(`${backendUrl}/submit`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const { job_id } = response.data;
      setJobId(job_id);
      setStatus('processing');
      pollStatus(job_id);
    } catch (err) {
      setError('Upload failed. Please try again.');
      setStatus('idle');
    }
  }, [beautifulMode]);

  const pollStatus = async (jobId: string) => {
    const interval = setInterval(async () => {
      try {
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
        const response = await axios.get(`${backendUrl}/status/${jobId}`);
        const { status: jobStatus } = response.data;
        if (jobStatus === 'completed') {
          const resultResponse = await axios.get(`${backendUrl}/result/${jobId}`);
          setResult(resultResponse.data);
          setStatus('completed');
          setProgress(100);
          clearInterval(interval);
        } else if (jobStatus === 'failed') {
          setError('Processing failed. Please try again.');
          setStatus('idle');
          clearInterval(interval);
        } else {
          setProgress(prev => Math.min(prev + 10, 90));
        }
      } catch (err) {
        setError('Status check failed.');
        setStatus('idle');
        clearInterval(interval);
      }
    }, 2000);
  };

  // Download MIDI and Sheet Music (to be implemented)
  const downloadMidi = () => {
    if (!result || !result.result || !result.result.notes) return;
    const notes = result.result.notes;
    const midi = new Midi();
    const track = midi.addTrack();
    notes.forEach((note: any) => {
      track.addNote({
        midi: note.pitch,
        time: note.start,
        duration: note.duration,
        velocity: note.velocity / 127,
      });
    });
    const blob = new Blob([midi.toArray()], { type: 'audio/midi' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dna_music_${jobId || 'output'}.mid`;
    a.click();
    URL.revokeObjectURL(url);
  };
  const downloadSheet = () => {
    if (!sheetSvg) return;
    const blob = new Blob([sheetSvg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dna_music_${jobId || 'output'}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/plain': ['.fasta', '.fastq', '.txt', '.fa'] },
    multiple: false,
  });

  const onTrySample = async () => {
    setStatus('uploading');
    setError(null);
    setProgress(0);
    try {
      const res = await fetch('/samples/long_music.fasta');
      const text = await res.text();
      setDnaSeq(text.replace(/[^ACGTacgt]/g, ''));
      const file = new File([text], 'long_music.fasta', { type: 'text/plain' });
      await onDrop([file]);
    } catch (err) {
      setError('Failed to load sample file.');
      setStatus('idle');
    }
  };

  return (
    <div className="min-h-screen bg-background-900 dark:bg-background-900 text-gray-900 dark:text-gray-100 transition-colors duration-500">
      <Hero onTrySample={onTrySample} />
      {/* Beautiful Mode Toggle */}
      <div className="flex items-center justify-center mb-6">
        <label className="flex items-center gap-2 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={beautifulMode}
            onChange={e => setBeautifulMode(e.target.checked)}
            className="form-checkbox h-5 w-5 text-primary-500 rounded focus:ring-primary-500 border-border bg-background-800"
          />
          <span className="text-gray-200 text-lg font-medium">Beautiful Mode</span>
        </label>
      </div>
      {/* Upload Area */}
      <form onSubmit={e => e.preventDefault()}>
        <div className="max-w-2xl mx-auto mb-8">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300 bg-background-800 dark:bg-background-800 border-border dark:border-dna-500 ${
              isDragActive
                ? 'border-accent-500 scale-105'
                : 'hover:border-dna-500'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="w-12 h-12 text-gray-500 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-200 mb-2">
              {isDragActive ? 'Drop your DNA file here' : 'Drag & drop your DNA file'}
            </p>
            <p className="text-sm text-gray-400">
              Supports FASTA, FASTQ, 23andMe, and raw text files
            </p>
          </div>
        </div>
      </form>
      {/* Progress */}
      <div className="max-w-2xl mx-auto mb-8">
        <div className="card bg-background-800 dark:bg-background-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-100">
              Processing your DNA...
            </h3>
            <span className="text-sm text-gray-400">
              {progress}%
            </span>
          </div>
          <div className="w-full bg-background-900 rounded-full h-2">
            <div
              className="bg-accent-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-400 mt-2">
            {status === 'uploading' && 'Uploading file...'}
            {status === 'processing' && 'Converting DNA to music...'}
            {status === 'completed' && 'Processing complete!'}
          </p>
        </div>
      </div>
      {/* Error */}
      {error && (
        <div className="max-w-2xl mx-auto mb-8">
          <div className="bg-red-900 border border-red-700 rounded-lg p-4">
            <p className="text-red-300">{error}</p>
          </div>
        </div>
      )}
      {/* Results */}
      {result && (
        <div className="max-w-4xl mx-auto">
          <div className="card bg-background-800 dark:bg-background-800">
            <h3 className="text-xl font-semibold text-gray-100 mb-4">
              Your Genetic Symphony
            </h3>
            {/* DNA Highlighter */}
            {dnaSeq && (
              <DNAHighlighter sequence={dnaSeq} currentIndex={currentNoteIdx} windowSize={3} />
            )}
            {/* Audio Player */}
            <AudioPlayer audioUrl={result.result.audio_path} />
            {/* Piano Roll */}
            <div className="mt-6">
              <h4 className="text-lg font-medium text-gray-100 mb-3">
                Musical Score
              </h4>
              <PianoRoll notes={result.result.notes || []} onSvgReady={setSheetSvg} />
            </div>
            {/* Download Options */}
            <div className="mt-6 flex gap-4">
              <button onClick={() => window.open(result.download_url, '_blank')} className="btn-primary">
                <Download className="w-4 h-4 mr-2" />
                Download WAV
              </button>
              <button onClick={downloadMidi} className="btn-secondary">
                <Download className="w-4 h-4 mr-2" />
                Download MIDI
              </button>
              <button onClick={downloadSheet} className="btn-accent">
                <Download className="w-4 h-4 mr-2" />
                Download Sheet Music
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 