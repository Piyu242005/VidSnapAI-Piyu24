<div align="center">

# 🎬 VidSnapAI
**Production-Ready AI-Powered Video Generation Engine**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Processing-green?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-AI_Voice-purple?style=for-the-badge&logo=sound-wave&logoColor=white)](https://elevenlabs.io/)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-blueviolet?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/research/whisper)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE.md)

VidSnapAI is a premium, AI-driven platform for automating the creation of high-impact short-form video content (Instagram Reels, TikToks, YouTube Shorts). By orchestrating intelligent **Whisper-powered subtitles**, **Beat-synced transitions**, and **Neural Speech AI**, it transforms base media into professional-quality social media campaigns at scale.

[🌟 Explore Demo](#-ui--design-highlights) • [🚀 Getting Started](#%EF%B8%8F-installation--setup) • [🗺️ Roadmap](ROADMAP.md) • [📄 API Docs](API.md)

</div>

---

## 📺 Demo & Previews

Experience the premium interface designed for high-conversion creator workflows:

| Home Dashboard | Video Generation | Image Gallery |
| :---: | :---: | :---: |
| ![Homepage](Screenshot%20Website/Homepage.jpeg) | ![Reel Created](Screenshot%20Website/Reel%20created.jpeg) | ![Reel Gallery](Screenshot%20Website/Reel%20Gallery.jpeg) |
| **Workspace Overview** | **Automated Pipeline** | **Content Management** |

*Also featuring beautifully crafted [About](templates/about.html) and [Features](templates/features.html) pages with complete cross-platform responsiveness.*

---

## ✨ Premium AI Features

VidSnapAI has evolved into a sophisticated AI editing suite:

*   🎙️ **Neural Voice Synthesis:** Deep generative speech integration powered by the **ElevenLabs API**, outputting ultra-realistic, studio-quality voiceovers.
*   🖋️ **Whisper Word-Sync Subtitles:** Automated transcription and captioning via **OpenAI Whisper**. Includes highlight pops and perfect alignment in social-safe zones.
*   🥁 **Beat-Synced Transitions:** Intelligent audio analysis (Python-based) that matches visual cuts and effects to the rhythm of your background music.
*   🔊 **Intelligent Audio Ducking:** Professional sound mixing that automatically lowers background music volume when the AI narrator is speaking.
*   🎞️ **CapCut-Style Visuals:** Programmatic FFmpeg pipelines handling zooms, pans, transitions, and overlays for maximum viewer retention.
*   🎨 **Premium UI/UX System:** High-fidelity scalable frontend featuring glassmorphism, fluid micro-animations, and dynamic theme switching (Midnight Crimson / Warm Vanilla).

---

## 🛠️ Technology Stack

| Architecture Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | `Flask (Python)` | Core application logic, routing, and HTTP orchestration. |
| **Video Engine** | `FFmpeg (Modular)` | Deterministic video composition, encoding, and filter chains. |
| **Transcription AI** | `OpenAI Whisper` | Neural speech-to-text for precise caption timing. |
| **Audio Intelligence** | `Librosa / Numpy` | Onset detection for beat-synchronization and ducking. |
| **AI Integration** | `ElevenLabs / Edge` | State-of-the-art Generative Text-to-Speech synthesis. |
| **Frontend Styling** | `HTML5 / Vanilla CSS` | Modern glassmorphism system with flexbox grids. |

---

## 🏗️ System Architecture

VidSnapAI employs a modular pipeline architecture for high-quality rendering:

1.  **Ingestion:** The frontend transmits prompt and media payloads to the Flask API.
2.  **Voice Generation:** The text payload is dispatched to the `text_to_audio` module for neural synthesis.
3.  **Intelligence Pipeline:** 
    - **Whisper Worker:** Transcribes generated audio into timed chunks for subtitles.
    - **Beat-Sync Worker:** Analyzes background music for optimal transition points.
4.  **FFmpeg Compositor:** The `video_processing` module multiplexes Voice, Music, Images, and Subtitles into a final `.mp4` container.
5.  **Delivery Interface:** The asset is delivered to the gallery dashboard asynchronously.

---

## 📁 Project Structure

```bash
VidSnapAI/
├── main.py                 # Core routing & application entry
├── generate_process.py     # Background worker & worker queue processor
├── text_to_audio.py        # ElevenLabs neural speech API abstractor
├── config.py               # Environment credentials
├── pipeline/               # 🚀 The AI Editing Engine 
│   ├── audio_processing.py # Ducking, fades, EQ mixing
│   ├── video_processing.py # Combiner and filter-chain mapping
│   ├── transitions.py      # Zooms, Xfades, Grading filters
│   ├── beat_sync.py        # Beat detection & temporal scaling
│   └── whisper_subtitles.py# ML-based word-sync generation
├── static/                 # Styles, Fonts, and Exported Reels
└── templates/              # Jinja2 layout engine views
```

---

## ⚙️ Installation & Setup

VidSnapAI is designed for rapid deployment. Follow these steps to initialize the services.

### Prerequisites
*   **Python:** Version 3.8 or higher.
*   **FFmpeg:** Core library installed and globally bound to your OS Path.
*   **ElevenLabs:** Valid API key (configure in `config.py`).

### Start Environment

**1. Clone the repository**
```bash
git clone https://github.com/Piyu242005/VidSnapAI.git
cd VidSnapAI
```

**2. Initialize virtual environment**
```bash
python -m venv .venv

# Windows activation
.\.venv\Scripts\activate
# Linux/MacOS activation
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run Application (Two Terminals)**
Terminal A: `python main.py`  
Terminal B: `python generate_process.py`

---

## 👨‍💻 Author

**Piyush Ramteke**  
*Data Scientist & Full Stack Developer*  
Architecting AI applications with premium SaaS interfaces.  

[<img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Profile"/>](https://github.com/Piyu242005)

---

<div align="center">

*Distributed under the [MIT License](LICENSE.md).*  
**Next-gen automation for the modern creator.**

</div>
