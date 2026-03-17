<div align="center">
  
#  VidSnapAI 

**AI-powered short-form video generation engine.** <br>
*Automate Instagram Reels, YouTube Shorts, and TikToks with AI.*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20Backend-lightgrey.svg)](https://flask.palletsprojects.com/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Video%20Engine-23211f.svg)](https://ffmpeg.org/)
[![AI TTS](https://img.shields.io/badge/TTS-ElevenLabs%20%7C%20Coqui-success.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---
</div>

##  Overview

**VidSnapAI** is a modern, production-grade video rendering engine that orchestrates the conversion of static images and text scripts into highly engaging, viral-ready short-form content. 

It leverages **FFmpeg** as a core manipulation tool to map audio, visual transitions, automated text timing, and AI text-to-speech generators.

###  Key Features
- ** CapCut-Style Editing Engine**: Intelligently handles alternating zooms, pans, dropshadows, and color correction to maximize viewer retention.
- ** Beat-Synced Flow**: Matches visual transitions exactly to the strong beats of your provided background music.
- ** Premium Voice Pipeline**: Supports auto-sync ducking (where background music intelligently lowers in volume while a narrator speaks).
- ** Whisper-Powered Subtitles**: Features automated word-sync logic generated via OpenAI's Whisper model. Applies highlight pops and perfectly aligns captions securely inside TikTok/IG viewing zones.
- ** Fully Modular Structure**: Extensible, well-documented Python pipeline.

---

##  Tech Stack

| Component | Technology | Purpose |
| --- | --- | --- |
| **Backend API** | Flask | Handles file ingestion, UI, and job orchestration |
| **Video Processing** | FFmpeg | Performs all complex filter chains and visual rendering |
| **Transcription** | OpenAI Whisper | Converts synthesized MP3s into timestamps for dynamic captions |
| **Beat Detection** | Librosa / Numpy | Performs onset detection for audio synchronization |
| **Voice / Speech** | ElevenLabs / Edge | Transforms provided scripts to highly realistic synthesized vocal tracks |

---

##  Quick Start

Follow these basic steps to get VidSnapAI running locally.

1. **Clone the repo**
   \\\ash
   git clone https://github.com/yourusername/VidSnapAI.git
   cd VidSnapAI
   \\\
2. **Setup virtual environment**
   \\\ash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   \\\
3. **Install**
   \\\ash
   pip install -r requirements.txt
   \\\

> **Note:** For detailed installation instructions including FFmpeg configuration, checkout the [Installation Guide](INSTALLATION.md)

---

##  Usage Flow

Generating your first automated reel requires two parallel processes:

**1. Run the Backend Generation Daemon:**
This continuously listens for new uploads and powers the FFmpeg logic pipeline.
\\\ash
python generate_process.py
\\\

**2. Run the Web Dashboard:**
A beautiful Flask UI to upload files and generate the script.
\\\ash
python main.py
\\\

> Jump to [Usage Guide](USAGE.md) for full context on submitting content!

---

##  Project Structure

\\\ash
 VidSnapAI
  main.py                  # User UI and endpoint mapping
  generate_process.py      # Core listener for triggering generations
  text_to_audio.py         # TTS bridging module
  pipeline/                # The AI Editing Engine 
     audio_processing.py  # Ducking, fades, EQ
     video_processing.py  # Combiner and exporter mapping
     transitions.py       # Zoompans, Xfades, Grading filters
     beat_sync.py         # Sub-beat audio tracking
     whisper_subtitles.py # Machine learning TTS-to-timestamp syncing
  user_uploads/            # Active workspace directories
  static/
      css/                 # Front-end styling (Red/Black modern theme)
      reels/               # Final MP4 export destination 
\\\

---

##  Architecture & Contributing
Want to dig deeper under the hood? Check out the specific logic flows in our [Architecture Documentation](ARCHITECTURE.md). 

Contributions make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**. Review our [Contribution Guidelines](CONTRIBUTING.md) to begin.

---

##  License
Distributed under the MIT License. See [LICENSE.md](LICENSE.md) for more information.

---
*Built with  for AI creators passing the threshold of automation.*
