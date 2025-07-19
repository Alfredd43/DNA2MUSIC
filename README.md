# dna2music

**Turn DNA into music using AI and modern web tech.**

---

## Features
- Upload DNA (FASTA, FASTQ, 23andMe, raw)
- Converts DNA to musical audio (WAV)
- FastAPI backend, Next.js frontend
- Real-time job status and download
- Beautiful and standard modes
- Docker & free-tier deploy ready

---

## Quickstart

**Backend:**
```sh
# Install Python deps
pip install -r backend/requirements.txt
# Start backend
uvicorn backend.main:app --reload
```

**Frontend:**
```sh
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## Usage
- Drag & drop your DNA file on the site
- Wait for processing (see progress)
- Listen or download your genetic symphony

---

## Project Structure
- `backend/` — FastAPI app, DNA/audio logic
- `frontend/` — Next.js app, UI
- `outputs/` — Generated audio files
- `samples/` — Example DNA files

---

## License
MIT. Use, remix, and extend freely. 