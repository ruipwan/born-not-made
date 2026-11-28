"""Render the return study from the artist-source directory used by gallery_cut.py."""
from pathlib import Path
import subprocess
import sys

sources = Path(sys.argv[1])
output = Path(sys.argv[2])
# At source cadence the first eight seconds occupy 240 frames.
# Preserve the final tank frame: its small silhouette crosses the larger outline.
rate = 30000 / 1001
opening = 240 / rate
tank_frames = 1151
tank_span = tank_frames / rate
filters = (
    "[0:v]trim=end_frame=240,setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos,setsar=1[a];"
    "[1:v]setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos,setsar=1[b];"
    "[2:v]trim=end_frame=270,setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos,setsar=1[c];"
    "[a][b][c]concat=n=3:v=1:a=0[picture];"
    f"[3:a]atrim=duration={tank_span},asetpts=PTS-STARTPTS,aresample=48000,"
    f"afade=in:d=0.12,afade=out:st={tank_span-0.18}:d=0.18,"
    f"adelay={round(opening*48000)}S:all=1,apad[audio]"
)
subprocess.run([
    "ffmpeg","-nostdin","-v","error","-y","-filter_complex_threads","3",
    "-ss","5.005","-i",str(sources/"ecology.mp4"),
    "-threads","3","-i",str(sources/"overhead-4k.mp4"),
    "-ss","18.018","-i",str(sources/"ecology.mp4"),
    "-i",str(sources/"overhead-audio.mp4"),
    "-filter_complex",filters,"-map","[picture]","-map","[audio]",
    "-shortest","-c:v","libx264","-threads","4","-preset","slow","-crf","28","-r","30000/1001",
    "-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-movflags","+faststart",
    "-t",str((240+tank_frames+270)/rate),str(output)
], check=True)
