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
from dotenv import load_dotenv
import redis

load_dotenv()
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def save_job(job_id, data):
    redis_client.hset(f"job:{job_id}", mapping=data)

def get_job(job_id):
    return redis_client.hgetall(f"job:{job_id}")

app = FastAPI(title="dna2music API", version="1.0.0")

# Serve audio files
app.mount("/files", StaticFiles(directory="outputs"), name="files")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/submit")
async def submit_dna(file: UploadFile, background_tasks: BackgroundTasks):
    allowed_types = ['.fasta', '.fastq', '.txt', '.fa']
    if not any(file.filename.endswith(ext) for ext in allowed_types):
        raise HTTPException(400, "Invalid file type. Supported: .fasta, .fastq, .txt, .fa")
    try:
        job_id = str(uuid.uuid4())
        file_content = await file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        job_data = {
            "status": "pending",
            "file_hash": file_hash,
            "filename": file.filename,
            "created_at": str(uuid.uuid4().time),
            "result": None,
            "error": None
        }
        save_job(job_id, job_data)
        background_tasks.add_task(process_dna_task, job_id, file_content, redis_client)
        return {
            "job_id": job_id,
            "status": "submitted",
            "message": "DNA file uploaded successfully. Processing started."
        }
    except UnicodeDecodeError:
        raise HTTPException(400, "File could not be decoded. Please upload a valid text file.")
    except Exception as e:
        raise HTTPException(500, f"Unexpected error: {str(e)}")

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job.get("status") == "completed":
        return {
            "job_id": job_id,
            "status": "completed",
            "result": json.loads(job["result"]) if job["result"] else None,
            "download_url": f"/download/{job_id}"
        }
    elif job.get("status") == "failed":
        return {
            "job_id": job_id,
            "status": "failed",
            "error": job.get("error")
        }
    else:
        return {
            "job_id": job_id,
            "status": job.get("status"),
            "message": "Processing in progress..."
        }

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return {
        "job_id": job_id,
        "status": job.get("status"),
        "created_at": job.get("created_at")
    }

@app.get("/download/{job_id}")
async def download_result(job_id: str):
    job = get_job(job_id)
    if not job or job.get("status") != "completed":
        raise HTTPException(404, "Result not available")
    result_path = f"outputs/{job_id}.wav"
    if not os.path.exists(result_path):
        raise HTTPException(404, "Audio file not found")
    return {"download_url": f"/files/{job_id}.wav"}

@app.get("/health")
async def health_check():
    # Count jobs in Redis (optional, can be slow for large sets)
    jobs_count = len(redis_client.keys("job:*"))
    return {"status": "healthy", "jobs_count": jobs_count}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 