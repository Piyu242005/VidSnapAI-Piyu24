# This file looks for new folders inside user uploads and converts them to reel if they are not already converted
import os 
import json
from text_to_audio import text_to_speech_file

import subprocess


def text_to_audio(folder):
    print("TTA - ", folder)
    with open(f"user_uploads/{folder}/desc.txt") as f:
        text = f.read()
    print(text, folder)
    text_to_speech_file(text, folder)

def create_reel(folder, settings=None):
    # Get absolute paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    input_file = os.path.join(base_dir, f"user_uploads/{folder}/input.txt")
    audio_file = os.path.join(base_dir, f"user_uploads/{folder}/audio.mp3")
    output_file = os.path.join(base_dir, f"static/reels/{folder}.mp4")
    
    # Load settings if not provided
    if settings is None:
        settings_file = os.path.join(base_dir, f"user_uploads/{folder}/settings.json")
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        else:
            settings = {}
    
    # Ensure static/reels directory exists
    os.makedirs(os.path.join(base_dir, "static/reels"), exist_ok=True)
    
    # Get aspect ratio and resolution
    aspect_ratio = settings.get('aspect_ratio', '9:16')
    quality = settings.get('quality', '1080p')
    
    if aspect_ratio == '9:16':
        width, height = 1080, 1920
    elif aspect_ratio == '16:9':
        width, height = 1920, 1080
    else:  # 1:1
        width, height = 1080, 1080
    
    if quality == '720p':
        if aspect_ratio == '9:16':
            width, height = 720, 1280
        elif aspect_ratio == '16:9':
            width, height = 1280, 720
        else:
            width, height = 720, 720
    
    # Build video filter
    vf_parts = [f"scale={width}:{height}:force_original_aspect_ratio=decrease"]
    vf_parts.append(f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black")
    
    # Add text overlay if specified
    overlay_text = settings.get('overlay_text', '')
    if overlay_text:
        overlay_position = settings.get('overlay_position', 'bottom')
        overlay_color = settings.get('overlay_color', '#ffffff')
        overlay_font = settings.get('overlay_font', 'Arial')
        overlay_size = settings.get('overlay_size', 40)
        
        # Calculate Y position
        if overlay_position == 'top':
            y_pos = 50
        elif overlay_position == 'center':
            y_pos = f'(h-text_h)/2'
        else:  # bottom
            y_pos = f'h-text_h-50'
        
        # Escape special characters in text
        overlay_text_escaped = overlay_text.replace("'", "\\'").replace(":", "\\:")
        
        # Add text overlay filter
        drawtext = f"drawtext=text='{overlay_text_escaped}':fontfile=/Windows/Fonts/{overlay_font}.ttf:fontsize={overlay_size}:fontcolor={overlay_color}:x=(w-text_w)/2:y={y_pos}"
        vf_parts.append(drawtext)
    
    video_filter = ','.join(vf_parts)
    
    # Build audio filter (for music mixing)
    music_file = settings.get('music_file', '')
    music_volume = settings.get('music_volume', 50) / 100.0
    
    if music_file:
        # Check if custom music or library music
        if settings.get('custom_music', False):
            music_path = os.path.join(base_dir, f"user_uploads/{folder}/{music_file}")
        else:
            music_path = os.path.join(base_dir, f"static/songs/{music_file}")
        
        if os.path.exists(music_path):
            # Mix audio tracks
            audio_filter = f"[0:a]volume=1.0[a1];[1:a]volume={music_volume}[a2];[a1][a2]amix=inputs=2:duration=first:dropout_transition=2"
            command = f'''ffmpeg -stream_loop -1 -f concat -safe 0 -i "{input_file}" -i "{audio_file}" -i "{music_path}" -vf "{video_filter}" -filter_complex "{audio_filter}" -c:v libx264 -c:a aac -r 30 -pix_fmt yuv420p -shortest -y "{output_file}"'''
        else:
            # Music file not found, use only voice
            command = f'''ffmpeg -stream_loop -1 -f concat -safe 0 -i "{input_file}" -i "{audio_file}" -vf "{video_filter}" -c:v libx264 -c:a aac -r 30 -pix_fmt yuv420p -shortest -y "{output_file}"'''
    else:
        # No music, use only voice
        command = f'''ffmpeg -stream_loop -1 -f concat -safe 0 -i "{input_file}" -i "{audio_file}" -vf "{video_filter}" -c:v libx264 -c:a aac -r 30 -pix_fmt yuv420p -shortest -y "{output_file}"'''
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FFmpeg Error: {result.stderr}")
        raise Exception(f"FFmpeg failed with error: {result.stderr}")
    
    print("CR - ", folder)


