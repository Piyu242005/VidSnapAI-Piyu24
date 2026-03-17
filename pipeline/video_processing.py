import subprocess
import os
from .audio_processing import process_audio
from .transitions import build_transition_complex_filter
from .subtitles import generate_subtitles_filter

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
    ffmpeg_inputs = [f"-i \"{img['file']}\"" for img in images_data]
    visual_filters = build_transition_complex_filter(images_data, width, height)
    
    # 3. Apply Subtitles
    overlay_font = settings.get('overlay_font', 'Arial')
    font_path = f"C:/Windows/Fonts/{overlay_font}.ttf"
    
    subtitles_str = generate_subtitles_filter(text_timing_data, font_path)
    
    if subtitles_str:
        visual_filters += f";[base_video]{subtitles_str}[final_video]"
        map_v = "[final_video]"
    else:
        map_v = "[base_video]"

    # 4. Final High-Quality Export Command
    inputs_cmd = " ".join(ffmpeg_inputs)
    
    # High quality settings for reels (-crf 18)
    command = (
        f"ffmpeg -y {inputs_cmd} -i \"{temp_audio_file}\" "
        f'-filter_complex "{visual_filters}" '
        f"-map {map_v} -map {len(images_data)}:a "
        f"-c:v libx264 -preset slow -crf 18 -profile:v high -level:v 4.2 "
        f"-pix_fmt yuv420p -color_range 1 -colorspace 1 -color_primaries 1 -color_trc 1 "
        f"-c:a aac -b:a 256k -shortest \"{output_file}\""
    )
    
    print("Compiling Reel with CapCut Editing Engine...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg pipeline fail: {result.stderr}")
    
    return output_file
