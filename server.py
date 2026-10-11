import json
import os
import shutil
import uuid
from typing import Optional
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from podcast.pipeline import PodcastPipeline
from podcast.voice_synthesizer import AVAILABLE_VOICES

app = FastAPI(title="Sarvam AI Podcast Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

# Store in-memory status for running jobs
generation_jobs = {}


@app.get("/")
def get_index():
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Web UI initializing..."}


@app.get("/api/voices")
def get_voices():
    return {
        "voices": [
            {"id": k, "name": k.title(), **v}
            for k, v in AVAILABLE_VOICES.items()
        ]
    }


@app.get("/api/episodes")
def list_episodes():
    episodes = []
    if os.path.exists(OUTPUT_DIR):
        for fname in os.listdir(OUTPUT_DIR):
            if fname.endswith("_transcript.json"):
                fpath = os.path.join(OUTPUT_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    audio_fname = fname.replace("_transcript.json", ".wav")
                    audio_exists = os.path.exists(os.path.join(OUTPUT_DIR, audio_fname))
                    created_time = os.path.getmtime(fpath)

                    episodes.append({
                        "id": fname.replace("_transcript.json", ""),
                        "topic": data.get("topic", "Untitled Episode"),
                        "duration_seconds": data.get("duration_seconds", 0),
                        "duration_formatted": f"{int(data.get('duration_seconds', 0)//60)}m {int(data.get('duration_seconds', 0)%60)}s",
                        "language": data.get("language", "English"),
                        "hosts": data.get("hosts", {}),
                        "audio_filename": audio_fname if audio_exists else None,
                        "transcript_filename": fname,
                        "created_at": created_time,
                        "dialogue_count": len(data.get("script", [])),
                    })
                except Exception:
                    pass

    # Sort newest first
    episodes.sort(key=lambda x: x["created_at"], reverse=True)
    return {"episodes": episodes}


@app.get("/api/audio/{filename}")
def stream_audio(filename: str):
    fpath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(fpath, media_type="audio/wav")


@app.get("/api/episode/{episode_id}")
def get_episode_details(episode_id: str):
    json_path = os.path.join(OUTPUT_DIR, f"{episode_id}_transcript.json")
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Episode not found")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["audio_url"] = f"/api/audio/{episode_id}.wav"
    return data


@app.post("/api/generate")
async def generate_podcast(
    topic: str = Form(...),
    language: str = Form("English"),
    language_code: str = Form("en-IN"),
    turns: int = Form(6),
    host_1_name: str = Form("Rohan"),
    host_1_voice: str = Form("rohan"),
    host_2_name: str = Form("Priya"),
    host_2_voice: str = Form("priya"),
    tone: str = Form("conversational, engaging, and lively"),
    bgm_style: str = Form("lofi_ambient"),
    file: Optional[UploadFile] = File(None),
):
    job_id = str(uuid.uuid4())[:8]
    doc_path = None

    if file and file.filename:
        safe_name = f"{job_id}_{file.filename}"
        doc_path = os.path.join(UPLOAD_DIR, safe_name)
        with open(doc_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    pipeline = PodcastPipeline(
        language_code=language_code,
        host_1_name=host_1_name,
        host_1_voice=host_1_voice,
        host_2_name=host_2_name,
        host_2_voice=host_2_voice,
        bgm_style=bgm_style,
    )

    try:
        result = pipeline.generate_episode(
            topic=topic,
            output_dir=OUTPUT_DIR,
            document_path=doc_path,
            num_turns=turns,
            language=language,
            tone=tone,
            enable_bgm=(bgm_style != "none"),
        )
        return {
            "success": True,
            "job_id": job_id,
            "episode": result,
            "audio_url": f"/api/audio/{result['audio_filename']}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
