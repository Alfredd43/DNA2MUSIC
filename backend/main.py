from fastapi import FastAPI, UploadFile, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from uuid import UUID
import hashlib
import json
from typing import Dict, Any
from dna2music.tasks import process_dna_task
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="dna2music API", version="1.0.0")

# Serve audio files
app.mount("/files", StaticFiles(directory="outputs"), name="files")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage (replace with Redis/DB in production)
jobs: Dict[str, Dict[str, Any]] = {}

@app.post("/submit")
async def submit_dna(file: UploadFile, background_tasks: BackgroundTasks):
    """Submit DNA file for processing"""
    
    # Validate file type
    allowed_types = ['.fasta', '.fastq', '.txt', '.fa']
    if not any(file.filename.endswith(ext) for ext in allowed_types):
        raise HTTPException(400, "Invalid file type. Supported: .fasta, .fastq, .txt, .fa")
    
    # Generate job ID and hash file for privacy
    job_id = str(uuid.uuid4())
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    # Store job info
    jobs[job_id] = {
        "status": "pending",
        "file_hash": file_hash,
        "filename": file.filename,
        "created_at": str(uuid.uuid4().time),  # Simplified timestamp
        "result": None,
        "error": None
    }
    
    # Start background processing
    background_tasks.add_task(process_dna_task, job_id, file_content, jobs)
    
    return {
        "job_id": job_id,
        "status": "submitted",
        "message": "DNA file uploaded successfully. Processing started."
    }

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    """Get processing result for a job"""
    
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    
    job = jobs[job_id]
    
    if job["status"] == "completed":
        return {
            "job_id": job_id,
            "status": "completed",
            "result": job["result"],
            "download_url": f"/download/{job_id}"
        }
    elif job["status"] == "failed":
        return {
            "job_id": job_id,
            "status": "failed",
            "error": job["error"]
        }
    else:
        return {
            "job_id": job_id,
            "status": job["status"],
            "message": "Processing in progress..."
        }

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Get job status"""
    
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    
    return {
        "job_id": job_id,
        "status": jobs[job_id]["status"],
        "created_at": jobs[job_id]["created_at"]
    }

@app.get("/download/{job_id}")
async def download_result(job_id: str):
    """Download processed audio file"""
    
    if job_id not in jobs or jobs[job_id]["status"] != "completed":
        raise HTTPException(404, "Result not available")
    
    # In production, serve from S3/Google Drive
    result_path = f"outputs/{job_id}.wav"
    if not os.path.exists(result_path):
        raise HTTPException(404, "Audio file not found")
    
    return {"download_url": f"/files/{job_id}.wav"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "jobs_count": len(jobs)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 