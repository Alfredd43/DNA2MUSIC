import create from 'zustand';

interface AppState {
  jobId: string | null;
  status: string;
  progress: number;
  result: any;
  error: string | null;
  beautifulMode: boolean;
  setJobId: (id: string | null) => void;
  setStatus: (status: string) => void;
  setProgress: (progress: number) => void;
  setResult: (result: any) => void;
  setError: (error: string | null) => void;
  setBeautifulMode: (mode: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  jobId: null,
  status: 'idle',
  progress: 0,
  result: null,
  error: null,
  beautifulMode: true,
  setJobId: (jobId) => set({ jobId }),
  setStatus: (status) => set({ status }),
  setProgress: (progress) => set({ progress }),
  setResult: (result) => set({ result }),
  setError: (error) => set({ error }),
  setBeautifulMode: (beautifulMode) => set({ beautifulMode }),
})); 