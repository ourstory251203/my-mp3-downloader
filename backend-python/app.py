from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import uuid
import shutil

app = FastAPI()

# Allow CORS from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# NEW: Add root route for GET and OPTIONS
@app.get("/")
def root():
    return {"message": "YouTube MP3 downloader backend is running."}

@app.options("/")
def options_root():
    return JSONResponse(status_code=204)

@app.post("/download")
async def download(request: Request):
    data = await request.json()
    url = data.get("url")

    if not url or "youtube.com/playlist" not in url:
        return JSONResponse(status_code=400, content={"error": "Invalid YouTube playlist URL"})

    download_id = str(uuid.uuid4())
    out_dir = f"/tmp/{download_id}"
    os.makedirs(out_dir, exist_ok=True)

    ytdlp_cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", f"{out_dir}/%(title)s.%(ext)s",
        url
    ]

    try:
        subprocess.run(ytdlp_cmd, check=True)
        zip_path = f"/tmp/{download_id}.zip"
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', out_dir)
        shutil.rmtree(out_dir)
        return FileResponse(zip_path, filename="playlist.zip")
    except subprocess.CalledProcessError:
        return JSONResponse(status_code=500, content={"error": "Failed to download playlist."})
