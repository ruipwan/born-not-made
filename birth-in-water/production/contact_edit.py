"""Extract two framings from the artist's same 4K overhead recording.
Usage: python contact_edit.py camera.mp4 camera_audio.mp4 contact-study.mp4
"""
import subprocess,sys
video,audio,dst=sys.argv[1:]
# Segment trims occur after a single seek/decode so the camera's clock survives
# the change in framing. The wide cut happens just after the gap becomes visible.
g="""[0:v]split=2[cu][ws];
[cu]trim=start=0:end=11.25,setpts=PTS-STARTPTS,crop=1440:810:1660:550,scale=1280:720:flags=lanczos[detail];
[ws]trim=start=11.25:end=20,setpts=PTS-STARTPTS,scale=1280:720:flags=lanczos[wide];
[detail][wide]concat=n=2:v=1:a=0,eq=saturation=0.89:contrast=1.018:brightness=0.006,setsar=1[v]"""
subprocess.run(['ffmpeg','-v','error','-y','-threads','3','-ss','15.15','-t','20','-i',video,
 '-ss','15.15','-t','20','-i',audio,'-filter_complex_threads','2','-filter_complex',g,'-map','[v]',
 '-map','1:a:0','-af','volume=12dB,afade=t=in:d=0.2,afade=t=out:st=19.6:d=0.4','-c:v','libx264',
 '-threads','3','-r','30000/1001','-pix_fmt','yuv420p','-crf','24','-preset','slow','-c:a','aac','-b:a','96k',
 '-movflags','+faststart',dst],check=True)
