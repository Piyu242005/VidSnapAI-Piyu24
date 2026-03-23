<div align="center">

# 🎬 VidSnapAI

**Production-Ready AI-Powered Video Generation Engine**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Processing-green?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-AI_Voice-purple?style=for-the-badge&logo=sound-wave&logoColor=white)](https://elevenlabs.io/)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-blueviolet?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/research/whisper)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE.md)

[🌟 Live Demo](#-demo) • [✨ Features](#-features) • [🚀 Installation](#-installation)

</div>

---

## 💡 Product Overview

VidSnapAI is a premium, AI-driven platform for automating the creation of high-impact short-form video content like Instagram Reels, TikToks, and YouTube Shorts. It's built for developers and content creators who need to generate professional videos at scale using intelligent transcription, dynamic transitions, and high-quality synthetic voice.

---

## ✨ Features

### 🧠 AI Features
*   🎙️ **Neural Voice Synthesis:** Studio-quality voiceovers powered by the ElevenLabs API.
*   🖋️ **Whisper Subtitles:** Automated word-sync transcription with OpenAI Whisper.

### 🎬 Video Processing
*   🥁 **Beat-Synced Transitions:** Intelligent audio analysis matching cuts to background music.
*   🔊 **Audio Ducking:** Professional sound mixing to balance background music and voice.
*   🎞️ **CapCut-Style Visuals:** Programmatic FFmpeg pipelines for dynamic visual transitions.

### 🎨 UI/UX
*   ✨ **Premium Dashboard:** High-fidelity scalable frontend with glassmorphism.
*   🌓 **Dynamic Theming:** Seamless switching between light and dark modes.

---

## 📺 Demo

| Home Dashboard | Video Generation | Image Gallery |
| :---: | :---: | :---: |
| <img src="Screenshot%20Website/Homepage.jpeg" alt="Homepage" width="100%" /> | <img src="Screenshot%20Website/Reel%20created.jpeg" alt="Reel Created" width="100%" /> | <img src="Screenshot%20Website/Reel%20Gallery.jpeg" alt="Reel Gallery" width="100%" /> |
| **Workspace Overview** | **Automated Pipeline** | **Content Management** |

---

## 🔄 Website Workflow

1. **Upload & Prompt:** Provide a topic/text prompt, and drop your base images into the intuitive creator dashboard.
2. **AI Generation & Processing:** The engine automatically synthesizes neural speech, calculates Whisper subtitle timings, and maps beat-synced transitions.
3. **Video Compositing:** Watch as FFmpeg seamlessly multiplexes voice, music, generated subtitles, and visual effects in the background.
4. **Export & Share:** Instantly preview and download your high-converting, professional MP4 directly from the integrated Gallery.

---

## 🏗️ Architecture

<p align="center">
  <img src="vidsnapai_full_workflow.svg" alt="VidSnapAI System Architecture & Workflow" width="100%" />
</p>

1. **Ingestion:** Frontend sends generation requests and media to the Flask API.
2. **Text-to-Speech:** Text payload is synthesized into neural speech via API.
3. **Transcription:** Audio is processed for accurate, word-synced subtitles.
4. **Beat-Sync:** Background music is analyzed for optimal visual transition points.
5. **Compositing:** Voice, music, media, and subtitles are multiplexed into an `.mp4` file.

---

## 🛠️ Tech Stack

| Tool | Purpose |
| :--- | :--- |
| **Flask** | Backend API & Orchestration |
| **FFmpeg** | Video compositing & processing |
| **Whisper** | AI Subtitle Generation |
| **ElevenLabs** | Neural Text-to-Speech |

---

## 📁 Project Structure

```bash
VidSnapAI/
├── main.py                 # Application entry point
├── generate_process.py     # Background worker logic
├── text_to_audio.py        # Speech generation interface
├── config.py               # Environment configuration
├── pipeline/               # Core AI editing engine modules
├── static/                 # Frontend assets (CSS, JS, Media)
└── templates/              # Jinja2 HTML templates
```

---

## 🚀 Installation

### Prerequisites
*   Python 3.8+
*   FFmpeg explicitly installed and added to PATH
*   ElevenLabs API Key

### Setup
```bash
# 1. Clone the repository
git clone https://github.com/Piyu242005/VidSnapAI.git
cd VidSnapAI

# 2. Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Or .\venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application (Requires 2 terminals)
# Terminal 1:
python main.py
# Terminal 2:
python generate_process.py
```

---

## 👨‍💻 Author

**Piyush Ramteke**
Data Scientist | AI Developer

[GitHub Profile](https://github.com/Piyu242005)