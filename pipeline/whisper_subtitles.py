import whisper
import torch

# global cache
_model = None

def get_model():
    global _model
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Whisper model on {device}...")
        _model = whisper.load_model("base", device=device)
    return _model

def highlight_text(text):
    words = text.split()
    return " ".join([
        w.upper() if i % 3 == 0 else w.capitalize()
        for i, w in enumerate(words)
    ])

def generate_srt(audio_path):
    """
    Uses OpenAI Whisper to transcribe the audio into timestamped subtitles.
    Returns sentence-level captions: [{"text": "...", "start": 0.0, "end": 2.3}]
    """
    print(f"Generating subtitles using Whisper for: {audio_path}")
    model = get_model()
    result = model.transcribe(audio_path, word_timestamps=False)
    
    segments = result.get("segments", [])
    subtitles = []
    
    for segment in segments:
        text = segment["text"].strip()
        start = float(segment["start"])
        end = float(segment["end"])
        
        # Clean punctuation to keep it modern and snappy
        text = text.replace(".", "").replace(",", "").replace("?", "").replace("!", "").replace('"', "")
        
        # Apply keyword styling (viral style logic)
        text = highlight_text(text)

        
        # Split very long sentences to keep them short for TikTok/Reels format
        words = text.split()
        if len(words) > 6:
            # Split into two lines if too long
            mid = len(words) // 2
            mid_time = start + (end - start) / 2
            
            subtitles.append({
                "text": " ".join(words[:mid]),
                "start": start,
                "end": mid_time
            })
            subtitles.append({
                "text": " ".join(words[mid:]),
                "start": mid_time,
                "end": end
            })
        else:
            subtitles.append({
                "text": text,
                "start": start,
                "end": end
            })
        
    return subtitles
