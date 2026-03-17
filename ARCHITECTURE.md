#  Architecture

VidSnapAI decouples standard linear video creation via an abstracted daemon pipeline logic map natively running over subprocess. This removes rendering wait bottlenecks from UI delivery components efficiently tying Text > Images > Voice > Video exactly into sync.

## The Core Pipeline

### 1. Ingestion Phase (main.py)
Flask serves a clean responsive upload panel that registers a POST request. Assets construct a unique UUID folder block mapped entirely inside user_uploads/.

### 2. Audio Bridging (	ext_to_audio.py + pipeline/whisper_subtitles.py)
- ElevenLabs immediately executes a .mp3 rendering based exclusively on user \desc.txt\ length. 
- OpenAI Whisper interprets exact sub-second timestamps across the mp3 structure.
- **Why?** It ensures text highlights match *spoken dialogue speeds* rather than visual frames.

### 3. Engine Transitions (pipeline/transitions.py + pipeline/beat_sync.py)
Librosa unpacks any applied music track directly scanning for audio burst thresholds (sr envelopes). 
Instead of blind 3-second holds, the images adapt to background audio tempos natively!
They are passed into CapCut-inspired math blocks calculating variables shifting:
- Alternating \zoompan\ arrays tracking iw/zoom.
- Abstract \xfade\ transition bridges dynamically covering the duration gap perfectly smoothing cuts organically. 

### 4. Audio Formatting & Ducking (pipeline/audio_processing.py)
Voice logic operates on a -map with compressor and sidechaincompress=threshold=-22dB. Result? Smooth premium radio-station ducking dropping backing track levels precisely exclusively during the timeframe speech occurs.

### 5. Final Export (pipeline/video_processing.py)
We link the arrays! We construct a final huge abstract string using yuv420p forcing -c:v libx264 -preset slow -crf 18. Executable natively by FFmpeg via OS path logic directly throwing the clean product out to static/reels.
