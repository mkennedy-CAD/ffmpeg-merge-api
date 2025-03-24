from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import uuid
import os
import subprocess

app = FastAPI()

@app.post("/merge")
async def merge_media(image: UploadFile = File(...), audio: UploadFile = File(...)):
    uid = str(uuid.uuid4())
    image_path = f"/tmp/{uid}_image.png"
    audio_path = f"/tmp/{uid}_audio.mp3"
    output_path = f"/tmp/{uid}_output.mp4"

    with open(image_path, "wb") as f:
        f.write(await image.read())

    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    command = [
        "ffmpeg",
        "-y",
        "-f", "lavfi", "-t", "2", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-i", audio_path,
        "-f", "lavfi", "-t", "2", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-i", audio_path,
        "-f", "lavfi", "-t", "2", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-loop", "1", "-i", image_path,
        "-filter_complex", "[0:a][1:a][2:a][3:a][4:a]concat=n=5:v=0:a=1[outa]",
        "-map", "5:v:0", "-map", "[outa]",
        "-t", "15",
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        output_path
    ]

    subprocess.run(command, check=True)

    return FileResponse(output_path, media_type="video/mp4", filename="output.mp4")
