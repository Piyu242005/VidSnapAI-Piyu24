import subprocess
import os
import logging
import time
from pathlib import Path
from .audio_processing import process_audio
from .transitions import build_transition_complex_filter
from .subtitles import generate_subtitles_filter

logger = logging.getLogger("vidsnapai.pipeline.video")

def create_premium_reel(folder_path, images_data, text_timing_data, settings):
    output_file = os.path.join(folder_path, "final_reel.mp4")
    temp_audio_file = os.path.join(folder_path, "mixed_audio.aac")
    
    voice_track = os.path.join(folder_path, "audio.mp3")
    
    base_dir = os.path.abspath(os.path.dirname(folder_path))
    music_file = settings.get('music_file', '')
    if music_file:
        if settings.get('custom_music', False):
            music_track = os.path.join(folder_path, music_file)
        else:
            proj_dir = os.path.dirname(base_dir)
            music_track = os.path.join(proj_dir, "static", "songs", music_file)
    else:
        music_track = ""

    # 1. Prepare Premium Audio (Voice Ducking, Normalization, Fades)
    process_audio(voice_track, music_track, temp_audio_file)
    
    # Calculate aspect ratio (default 9:16)
    aspect_ratio = settings.get('aspect_ratio', '9:16')
    quality = settings.get('quality', '1080p')
    width, height = 1080, 1920
    if aspect_ratio == '16:9':
        width, height = 1920, 1080
    elif aspect_ratio == '1:1':
        width, height = 1080, 1080
    if quality == '720p':
        width = int(width * 720 / max(width, height))
        height = int(height * 720 / max(width, height))

    # 2. Prepare Dynamic Visuals & Transitions (CapCut Style)
    ffmpeg_inputs = []
    for img in images_data:
        ffmpeg_inputs.extend(["-i", os.path.abspath(img["file"])])
    visual_filters = build_transition_complex_filter(images_data, width, height)
    
    # 3. Apply Subtitles
    overlay_font = settings.get('overlay_font', 'Arial')
    configured_font = os.getenv("VIDSNAPAI_FONT_PATH")
    candidates = [configured_font, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf", f"C:/Windows/Fonts/{overlay_font}.ttf"]
    font_path = next((candidate for candidate in candidates if candidate and Path(candidate).is_file()), "")
    
    subtitles_str = generate_subtitles_filter(text_timing_data, font_path)
    
    if subtitles_str:
        visual_filters += f";[base_video]{subtitles_str}[final_video]"
        map_v = "[final_video]"
    else:
        map_v = "[base_video]"

    # 4. Final High-Quality Export Command
    command = [
        "ffmpeg", "-y", *ffmpeg_inputs, "-i", os.path.abspath(temp_audio_file),
        "-filter_complex", visual_filters,
        "-map", map_v, "-map", f"{len(images_data)}:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-level:v", "4.2",
        "-pix_fmt", "yuv420p", "-color_range", "1", "-colorspace", "1", "-color_primaries", "1", "-color_trc", "1",
        "-c:a", "aac", "-b:a", "256k", "-shortest", os.path.abspath(output_file),
    ]

    logger.info("Compiling Reel with CapCut Editing Engine")
    started = time.monotonic()
    try:
        result = subprocess.run(command, shell=False, capture_output=True, text=True,
            timeout=int(os.getenv("FFMPEG_TIMEOUT_SECONDS", "1800")))
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg timed out after %.2fs", time.monotonic() - started)
        raise
    duration = time.monotonic() - started
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()[-4000:]
        logger.error("FFmpeg failed returncode=%s duration=%.2fs stderr=%s",
                     result.returncode, duration, stderr)
        raise RuntimeError("FFmpeg pipeline failed")
    logger.info("FFmpeg completed returncode=%s duration=%.2fs", result.returncode, duration)
    
    return output_file
