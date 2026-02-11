"""
VEDA API - FastAPI REST endpoints for video generation.

Run with:
    python -m veda_app.api
    # or
    uvicorn veda_app.api:app --host 0.0.0.0 --port 8000
"""

import uuid
import time
import logging
import threading
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

logger = logging.getLogger("VEDA.api")

# ─── Pydantic Models ───────────────────────────────────────────

class GenerateRequest(BaseModel):
    """Request body for video generation."""
    prompt: str = Field(..., description="Text prompt for video generation")
    style: str = Field("cinematic", description="Style preset")
    seed: Optional[int] = Field(None, description="Random seed")
    upscale: bool = Field(False, description="Upscale with Real-ESRGAN 4x")
    num_frames: Optional[int] = Field(None, description="Override frame count")


class JobResponse(BaseModel):
    """Response with job info."""
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Response for job status query."""
    job_id: str
    status: str
    progress: Optional[str] = None
    result_path: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: Optional[float] = None


class StylesResponse(BaseModel):
    """Response listing available styles."""
    styles: list


# ─── Job Store ─────────────────────────────────────────────────

@dataclass
class Job:
    """Internal job tracking."""
    job_id: str
    prompt: str
    style: str
    seed: Optional[int]
    upscale: bool
    num_frames: Optional[int]
    status: str = "queued"
    result_path: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    duration_seconds: float = 0.0


class JobStore:
    """Thread-safe in-memory job store."""
    
    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
    
    def create(self, **kwargs) -> Job:
        job_id = str(uuid.uuid4())[:8]
        job = Job(job_id=job_id, **kwargs)
        with self._lock:
            self._jobs[job_id] = job
        return job
    
    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)
    
    def update(self, job_id: str, **kwargs) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                for k, v in kwargs.items():
                    setattr(job, k, v)


# ─── Background Worker ────────────────────────────────────────

def _worker(job: Job, store: JobStore):
    """Run generation in a background thread."""
    from veda_engine.config import VEDAConfig
    from veda_engine.generators import TextToVideoGenerator
    
    store.update(job.job_id, status="running")
    start = time.time()
    
    try:
        config = VEDAConfig.for_gtx_1650()
        
        # Override frames if specified
        if job.num_frames:
            config.num_frames = job.num_frames
        
        generator = TextToVideoGenerator(config)
        
        # Generate output path
        output_dir = Path("outputs/api")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{job.job_id}.mp4"
        
        result = generator.generate(
            prompt=job.prompt,
            output_path=str(output_path),
            style=job.style,
            seed=job.seed,
            upscale=job.upscale,
        )
        
        duration = round(time.time() - start, 1)
        store.update(
            job.job_id,
            status="completed",
            result_path=str(result),
            duration_seconds=duration,
        )
        logger.info(f"Job {job.job_id} completed in {duration}s")
        
    except Exception as e:
        duration = round(time.time() - start, 1)
        store.update(
            job.job_id,
            status="failed",
            error=str(e),
            duration_seconds=duration,
        )
        logger.error(f"Job {job.job_id} failed: {e}")


# ─── FastAPI App ───────────────────────────────────────────────

app = FastAPI(
    title="VEDA Video Generation API",
    description="AI-powered video generation engine — REST API",
    version="0.2.0",
)

store = JobStore()


@app.get("/")
async def root():
    """API info endpoint."""
    return {
        "name": "VEDA API",
        "version": "0.2.0",
        "docs": "/docs",
        "endpoints": [
            "POST /api/generate",
            "GET /api/status/{job_id}",
            "GET /api/download/{job_id}",
            "GET /api/styles",
        ]
    }


@app.post("/api/generate", response_model=JobResponse)
async def generate(request: GenerateRequest):
    """
    Submit a video generation job.
    Returns immediately with a job_id for polling.
    """
    job = store.create(
        prompt=request.prompt,
        style=request.style,
        seed=request.seed,
        upscale=request.upscale,
        num_frames=request.num_frames,
    )
    
    # Start generation in background thread
    thread = threading.Thread(
        target=_worker,
        args=(job, store),
        daemon=True,
    )
    thread.start()
    
    logger.info(f"Job {job.job_id} submitted: {request.prompt[:50]}...")
    
    return JobResponse(
        job_id=job.job_id,
        status="queued",
        message=f"Job submitted. Poll GET /api/status/{job.job_id} for progress.",
    )


@app.get("/api/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    """Get the current status of a generation job."""
    job = store.get(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        result_path=job.result_path,
        error=job.error,
        duration_seconds=job.duration_seconds if job.duration_seconds > 0 else None,
    )


@app.get("/api/download/{job_id}")
async def download(job_id: str):
    """Download a completed video."""
    job = store.get(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if job.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} is not completed (status: {job.status})"
        )
    
    if not job.result_path or not Path(job.result_path).exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        path=job.result_path,
        media_type="video/mp4",
        filename=f"veda_{job_id}.mp4",
    )


@app.get("/api/styles", response_model=StylesResponse)
async def list_styles():
    """List available style presets."""
    from veda_engine.core.prompt_brain import PromptBrain
    
    brain = PromptBrain()
    return StylesResponse(styles=brain.get_styles())


# ─── CLI Runner ────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    
    print("\n🎬 VEDA API Server")
    print("=" * 40)
    print("  Docs:  http://localhost:8000/docs")
    print("  API:   http://localhost:8000/api/")
    print("=" * 40 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
