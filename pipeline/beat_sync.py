import librosa
import numpy as np

def detect_beats(audio_path):
    """
    Detects beats in the background music to drive image transitions.
    Returns a list of beat timestamps in seconds.
    """
    try:
        y, sr = librosa.load(audio_path)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        
        beat_times = list(librosa.frames_to_time(beats, sr=sr))
        # Snap images to strongest beats (reduces frenetic jumping)
        return beat_times[::2] if beat_times else []
    except Exception as e:
        print(f"Beat sync disabled or failed: {e}")
        return []

def apply_beat_sync_durations(images_data, beat_times, total_duration):
    """
    Adjusts the 'duration' property of each image to align with detected beats.
    CapCut style syncing to major beats.
    """
    if not beat_times:
        # Fallback to evenly spaced 1.5s intervals if no beats detected
        beat_times = [i * 1.5 for i in range(int(total_duration) + 2)]

    # Map image transitions to detected beats
    num_images = len(images_data)
    
    # Filter beats that are within the total video duration
    valid_beats = [b for b in beat_times if b < total_duration]
    
    if len(valid_beats) < num_images:
        # Generate artificial beats if there aren't enough
        step = total_duration / num_images
        valid_beats = [i * step for i in range(num_images)]
    
    # Pick beats evenly distributed depending on number of images
    step = max(1, len(valid_beats) // num_images)
    selected_beats = [valid_beats[i * step] for i in range(num_images)]
    selected_beats.append(total_duration) # Add end boundary
    
    for i in range(num_images):
        duration = selected_beats[i+1] - selected_beats[i]
        # Enforce minimum and maximum duration for good pacing
        duration = max(min(duration, 3.0), 0.5)
        images_data[i]['duration'] = duration
        
    return images_data
