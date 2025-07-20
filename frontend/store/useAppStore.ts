import create from 'zustand';

// Define the structure of the API result object
export interface Note {
  pitch: number;
  start: number;
  duration: number;
  velocity: number;
}

export interface ApiResult {
  result: {
    notes: Note[];
    audio_path: string;
    [key: string]: any; // for any extra fields
  };
  download_url?: string;
  [key: string]: any; // for any extra fields
}

interface AppState {
  jobId: string | null;
  status: string;
  progress: number;
  result: ApiResult | null;
  error: string | null;
  beautifulMode: boolean;
  dnaSeq: string;
  sheetSvg: string | null;
  setJobId: (id: string | null) => void;
  setStatus: (status: string) => void;
  setProgress: (progress: number) => void;
  setResult: (result: ApiResult | null) => void;
  setError: (error: string | null) => void;
  setBeautifulMode: (mode: boolean) => void;
  setDnaSeq: (seq: string) => void;
  setSheetSvg: (svg: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  jobId: null,
  status: 'idle',
  progress: 0,
  result: null,
  error: null,
  beautifulMode: true,
  dnaSeq: '',
  sheetSvg: null,
  setJobId: (jobId) => set({ jobId }),
  setStatus: (status) => set({ status }),
  setProgress: (progress) => set({ progress }),
  setResult: (result) => set({ result }),
  setError: (error) => set({ error }),
  setBeautifulMode: (beautifulMode) => set({ beautifulMode }),
  setDnaSeq: (dnaSeq) => set({ dnaSeq }),
  setSheetSvg: (sheetSvg) => set({ sheetSvg }),
})); 