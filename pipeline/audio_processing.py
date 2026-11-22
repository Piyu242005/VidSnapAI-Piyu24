import os
import subprocess
import logging
import time

logger = logging.getLogger("vidsnapai.pipeline.audio")

def process_audio(voice_file, music_file, output_audio, max_duration=None):
    """
    Enhances audio, normalizes voiceover, and applies background music ducking.
    Adds slight fade in/out for professional sound.
    """
    if not os.path.exists(voice_file):
        raise FileNotFoundError(f"Voiceover track missing: {voice_file}")

    filters = []
    inputs = ["-i", os.path.abspath(voice_file)]

    # Standardize voice channel, normalize loudness, add subtle compression
    filters.append("[0:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,acompressor=threshold=-15dB:ratio=4:attack=5:release=50[voice]")
    
    if music_file and os.path.exists(music_file):
        inputs.append("-i")
        inputs.append(os.path.abspath(music_file))
        
        # Loop music, add ducking taking [voice] as sidechain
        # We also apply a subtle fade-in to the music to prevent harsh starts
        filters.append("[1:a]aloop=loop=-1:size=2e+09,volume=0.35,afade=t=in:st=0:d=2[music];"
                       "[music][0:a]sidechaincompress=threshold=-22dB:ratio=4.0:attack=10:release=200:makeup=1.5[bgm];"
                       "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2,volume=1.0[aout]")
        map_arg = "-map [aout]"
    else:
        filters.append("[0:a]volume=1.2[aout]")
        map_arg = "-map [aout]"

    filter_complex = ";".join(filters)
    
    # Clip duration if audio shouldn't exceed max length
    command = ["ffmpeg", "-y", *inputs, "-filter_complex", filter_complex]
    command.extend(map_arg.split())
    if max_duration:
        command.extend(["-t", str(max_duration)])
    command.extend(["-c:a", "aac", "-b:a", "256k", os.path.abspath(output_audio)])
    started = time.monotonic()
    result = subprocess.run(command, shell=False, capture_output=True, text=True,
                            timeout=int(os.getenv("FFMPEG_TIMEOUT_SECONDS", "1800")))
    duration = time.monotonic() - started
    if result.returncode != 0:
        logger.error("FFmpeg audio failed returncode=%s duration=%.2fs stderr=%s",
                     result.returncode, duration, (result.stderr or "").strip()[-4000:])
        raise RuntimeError("FFmpeg audio pipeline failed")
    
    return output_audio
