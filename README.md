<h1 align="center">🎵 dna2music</h1>

<p align="center">
  <b>AI-powered DNA-to-music converter</b><br>
  🎶 Turn your genetic code into music | ⚡ FastAPI backend + Next.js frontend | 🧬 Real-time, beautiful sonification
</p>

---

## ✨ Overview

**dna2music** is a production-ready DNA-to-music web app and API. Upload your DNA (FASTA, FASTQ, 23andMe, or raw), and get a unique musical composition—instantly!

- ✅ Converts DNA to musical audio (WAV)
- ✅ Real-time job status and download
- ✅ Beautiful and standard mapping modes
- ✅ Modern FastAPI backend + Next.js frontend
- ✅ Docker & free-tier deploy ready

---

## 🚀 Features

- 🧬 **DNA File Support** – FASTA, FASTQ, 23andMe, and raw text
- 🎹 **Musical Mapping** – Chords, notes, and rhythm from your sequence
- 🎧 **Instant Audio** – Download or play your genetic symphony (WAV)
- 🌈 **Beautiful Mode** – Pentatonic/major scale for pleasing melodies
- 🔄 **Live Progress** – See upload and processing status in real time
- 🖥️ **Modern UI** – Next.js + Tailwind, responsive and dark mode
- 🐳 **Docker-Ready** – One command to run everything

---

## 🛠️ Tech Stack

| Layer        | Technology           |
|--------------|----------------------|
| 🎯 Backend   | FastAPI + Python     |
| 🎼 Music     | NumPy, SoundFile, custom mapping |
| 🖥️ Frontend  | Next.js (React), Tailwind CSS |
| 🐳 Deploy    | Docker, Docker Compose |

---

## 🧪 Example Workflow

1. Upload your DNA file via the web UI.
2. Backend parses, analyzes, and maps DNA to music.
3. Audio is generated and made available for download/playback.
4. View a piano roll of your sequence’s musical score.

---

## 🧰 Usage

### 🔧 Installation

```bash
git clone https://github.com/Alfredd43/DNA2MUSIC.git
cd DNA2MUSIC

# Backend
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload

# Frontend (in a new terminal)
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📂 Project Structure

- `backend/` — FastAPI app, DNA/audio logic
- `frontend/` — Next.js app, UI
- `dna2music/` — Core mapping, models, and tasks
- `outputs/` — Generated audio files
- `samples/` — Example DNA files

---

## 🪪 License
MIT. Use, remix, and extend freely. 