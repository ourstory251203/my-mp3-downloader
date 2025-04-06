from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import yt_dlp
import os
import uuid

app = FastAPI()

class PlaylistRequest(BaseModel):
    url: str

@app.post("/download")
async def download_playlist(req: PlaylistRequest):
    playlist_url = req.url
    if "youtube.com" not in playlist_url:
        return JSONResponse({"error": "Invalid YouTube URL"}, status_code=400)

    download_id = str(uuid.uuid4())
    download_dir = f"/tmp/{download_id}"
    os.makedirs(download_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    # Optional: zip the files and return the zip
    zip_path = f"{download_dir}.zip"
    os.system(f"zip -r {zip_path} {download_dir}")

    return FileResponse(zip_path, filename="playlist.zip", media_type='application/zip')
