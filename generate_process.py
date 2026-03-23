# This file looks for new folders inside user uploads and converts them to reel 
# if they are not already converted                                               
import os 
import json
import shutil
from text_to_audio import text_to_speech_file as tta_core
from pipeline.video_processing import create_premium_reel
from pipeline.whisper_subtitles import generate_srt
from pipeline.beat_sync import detect_beats, apply_beat_sync_durations
import urllib.parse

def text_to_audio(folder):
    print("TTA - ", folder)
    with open(f"user_uploads/{folder}/desc.txt", encoding="utf-8") as f:
        text = f.read()
    print(text, folder)
    tta_core(text, folder)

def parse_input_txt(input_file, folder_dir):
    images_data = []
    if not os.path.exists(input_file):
        return images_data
        
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_file = None
    for line in lines:
        line = line.strip()
        if line.startswith("file "):
            # Format: file 'filename.jpg'
            fname = line.replace("file ", "").strip("'").strip('"')
            current_file = os.path.join(folder_dir, fname)
        elif line.startswith("duration "):
            dur = float(line.replace("duration ", ""))
            if current_file:
                images_data.append({"file": current_file, "duration": dur})
                current_file = None
    return images_data

def create_reel(folder, settings=None):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    folder_dir = os.path.join(base_dir, f"user_uploads/{folder}")
    
    if settings is None:
        settings_file = os.path.join(folder_dir, "settings.json")
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        else:
            settings = {}

    desc_file = os.path.join(folder_dir, "desc.txt")
    if os.path.exists(desc_file):
        with open(desc_file, "r", encoding="utf-8", errors="ignore") as f:
            full_text = f.read()
    else:
        full_text = "Watch this amazing reel"
        

    audio_file = os.path.join(folder_dir, "audio.mp3")
    
    # We can detect background music beats for transitions
    music_file_name = settings.get('music_file', '')
    music_track = ""
    if music_file_name:
        if settings.get('custom_music', False):
            music_track = os.path.join(folder_dir, music_file_name)
        else:
            music_track = os.path.join(base_dir, "static", "songs", music_file_name)
            
    beat_times = []
    if music_track and os.path.exists(music_track):
        beat_times = detect_beats(music_track)

    input_file = os.path.join(folder_dir, "input.txt")
    images_data = parse_input_txt(input_file, folder_dir)
        
    # Get audio duration theoretically (simplified, or use ffprobe)
    # Whisper will get the actual times.
    
    # Generate Subtitles & Get Total Duration from Voice
    text_timing_data = generate_srt(audio_file)
    
    if text_timing_data:
        # Give small buffer after last speech
        total_audio_duration = text_timing_data[-1]['end'] + 1.0 
    else:
        # Fallback if no voice
        total_audio_duration = len(images_data) * 2.5
        
    # Inject Viral Hook
    text_timing_data.insert(0, {
        "text": "🔥 WAIT FOR THIS...",
        "start": 0.0,
        "end": 2.0
    })
        
    # Sync images to beats
    images_data = apply_beat_sync_durations(images_data, beat_times, total_audio_duration)
    
    output_tmp = create_premium_reel(folder_dir, images_data, text_timing_data, settings)
    
    output_file_final = os.path.join(base_dir, f"static/reels/{folder}.mp4")
    shutil.move(output_tmp, output_file_final)
    
    print("CR - ", folder)


if __name__ == '__main__':
    import time
    print("VidSnapAI Premium Background Processor Started...")

    while True:
        try:
            if not os.path.exists("user_uploads"):
                os.makedirs("user_uploads", exist_ok=True)

            folders = [f for f in os.listdir("user_uploads") if os.path.isdir(os.path.join("user_uploads", f))]
            for folder in folders:
                if folder.startswith('temp_'):
                    continue

                output_file = f"static/reels/{folder}.mp4"
                if not os.path.exists(output_file):
                    desc_file = f"user_uploads/{folder}/desc.txt"
                    input_file = f"user_uploads/{folder}/input.txt"

                    if os.path.exists(desc_file) and os.path.exists(input_file):
                        print(f"Processing new folder: {folder}")
                        try:
                            audio_file = f"user_uploads/{folder}/audio.mp3"
                            if not os.path.exists(audio_file):
                                text_to_audio(folder)

                            create_reel(folder)
                            print(f"Successfully processed: {folder}")
                        except Exception as e:
                            print(f"Error processing {folder}: {e}")

            time.sleep(5)
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(10)
