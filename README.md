<div align="center">

# 🎬 VidSnapAI
**Production-Ready AI-Powered Video Form Content Generation Platform**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Processing-green?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-AI_Voice-purple?style=for-the-badge&logo=sound-wave&logoColor=white)](https://elevenlabs.io/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

VidSnapAI is a production-ready, AI-powered platform designed to fully automate the creation of highly engaging short-form video content (Instagram Reels, TikToks, YouTube Shorts). By orchestrating intelligent text-to-speech AI voice synthesis with programmatic FFmpeg video assembly, it transforms basic text scripts and static imagery into professional-quality social media video campaigns at scale.

[🌟 Explore Demo](#-ui--design-highlights) • [🚀 Getting Started](#%EF%B8%8F-installation--setup) • [🗺️ Roadmap](#-future-improvements)

</div>

---

## 📺 Demo & Previews

Experience the premium interface designed for high-conversion creator workflows:

| Home Dashboard | Video Generation | Image Gallery |
| :---: | :---: | :---: |
| ![Homepage](Screenshot%20Website/Homepage.jpeg) | ![Reel Created](Screenshot%20Website/Reel%20created.jpeg) | ![Reel Gallery](Screenshot%20Website/Reel%20Gallery.jpeg) |
| **Workspace Overview** | **Automated Pipeline** | **Content Management** |

*Also featuring beautifully crafted [About](Screenshot%20Website/About.jpeg) and [Features](Screenshot%20Website/Features.jpeg) pages with complete cross-platform responsiveness.*

---

## ✨ Enterprise-Grade Features

*   🎙️ **AI Voice Synthesis:** Deep generative speech integration powered by the ElevenLabs API, outputting ultra-realistic, studio-quality voiceovers.
*   🎞️ **Automated Video Editing:** Powerful programmatic video compilation pipelines leveraging FFmpeg to handle complex logic, transitions, audio mixing, and image stitching seamlessly.
*   🖼️ **Smart Media Pipeline:** Intelligent image upload parsing and temporal scaling to perfectly match generated speech audio lengths.
*   🗂️ **Content Management Gallery:** Advanced, asynchronous generation gallery allowing users to view, manage, and download generated media workflows.
*   📱 **Platform Optimized Ratios:** Native generation of vertical video formats (9:16 aspect ratio) uniquely tuned for the modern social media ecosystem algorithm.
*   🎨 **Premium UI/UX System:** High-fidelity scalable frontend featuring real-time glassmorphism data rendering, fluid micro-animations, and complete responsive layout controls.

---

## 🛠️ Technology Stack

| Architecture Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | `Flask (Python)` | Core application logic, routing, and HTTP orchestration. |
| **Video Engine** | `FFmpeg (moviepy)` | Heavy-lifting deterministic video composition and encoding. |
| **AI Integration** | `ElevenLabs API` | State-of-the-art Generative Text-to-Speech synthesis. |
| **Frontend Styling** | `HTML5/CSS3` | Modern glassmorphism system with flexbox grids. |
| **Client Scripting** | `Vanilla ES6 JS` | Asynchronous file handling and UI state management. |

---

## 🏗️ System Architecture

VidSnapAI employs a decoupled monolithic architecture. When a user creates a new campaign:
1.  **Ingestion:** The frontend transmits the prompt and selected media payloads securely to the backend routing layer.
2.  **Voice Generation Pipeline:** The text payload is dispatched to the `text_to_audio` module, negotiating a secure stream with the ElevenLabs inference engine.
3.  **Video Processing Pipeline:** A background generation loop (`generate_process.py`) captures the audio stream length and parameters, parsing them to `moviepy`/`FFmpeg`. Static assets are temporally mapped, and multiple streams (Voice, Image, Transitions) are multiplexed into a single `.mp4` container.
4.  **Delivery Interface:** The highly optimized asset is delivered to the gallery dashboard via a secure, unblocked asynchronous view state.

---

## 📁 Project Structure

```bash
VidSnapAI/
├── main.py                 # Core routing, server configuration & application entry
├── generate_process.py     # Asynchronous video multiplexing & worker queue processor
├── text_to_audio.py        # ElevenLabs neural speech API abstractor
├── config.py               # Application-level environment definitions
├── requirements.txt        # Python dependency manifest
├── static/                 # Ephemeral & persistent static assets
│   ├── css/                # Component & global stylesheets 
│   ├── js/                 # Client state & theme toggle controllers
│   └── fonts/              # Typography distribution
├── templates/              # Jinja2 layout engine views
│   ├── index.html          # Main workspace portal
│   ├── create.html         # Media processing ingest form
│   └── about.html          # Creator/Team information view
└── user_uploads/           # Sandbox for unprocessed media staging
```

---

## ⚙️ Installation & Setup

VidSnapAI is designed for rapid deployment. Follow these steps to initialize the core services on your local machine.

### Prerequisites
*   **Python:** Version 3.8 or higher.
*   **FFmpeg:** Core library installed and globally bound to your OS Path. [Download FFmpeg](https://ffmpeg.org/download.html)
*   **ElevenLabs:** Valid API key. [Get Key Here](https://elevenlabs.io/)

### Start Environment

**1. Clone the master repository**
```bash
git clone https://github.com/Piyu242005/VidSnapAI.git
cd VidSnapAI
```

**2. Initialize isolated virtual environment**
```bash
python -m venv .venv

# Windows activation
.\.venv\Scripts\activate
# Linux/MacOS activation
source .venv/bin/activate
```

**3. Inject dependencies via PIP**
```bash
pip install -r requirements.txt
```

**4. Configure Environment Credentials**
*   Inject your ElevenLabs API key into the `config.py` definitions file.

**5. Boot Application Web Server**
```bash
python main.py
```

**6. Boot Background Video Processor (Open a new terminal)**
```bash
# Don't forget to activate your virtual environment in this new terminal
python generate_process.py
```
> **Notice:** The generator script functions as the core asynchronous worker. Without it, videos will remain in the processing staging queue.

---

## 💡 Usage Workflow

Creating high-performing content operates in three modular steps:
1.  **Navigate to Workspace:** Click "Create New Reel" on the dashboard UI.
2.  **Data Ingest:** Provide your desired high-impact text script and upload relevant background visual imagery.
3.  **Execute & Retrieve:** Submit the generation request. The AI and rendering pipelines will compile your Reel in seconds. Navigate to the Gallery to preview or export the final `mp4` asset.

---

## 🎨 UI & Design Highlights

VidSnapAI implements a highly scalable, premium visual system built on modern design principles:
*   **Agnostic Theme Toggling:** Live shifting between dynamic visual identities stored securely in browser `LocalStorage`.
*   **Midnight Crimson:** A deep-black dark mode accentuated with vibrant neon red (`#ff0000`) for high-contrast focus.
*   **Warm Vanilla:** An inviting soft-beige light mode (`#fdfcfb` → `#e2d1c3`) rendering dark professional typography.
*   **Glassmorphism Engine:** Translucent background blurring across modal components delivering a sensation of immense visual depth.

---

## 🚀 Future Improvements (Roadmap)

VidSnapAI is under active, aggressive development to scale its operations to enterprise production standards:

*   [ ] **FastAPI Migration:** Complete architectural transition to Python's fastest asynchronous framework (ASGI) to handle 10x concurrent generation queues.
*   [ ] **Machine Learning Enhancements:** Implementation of localized, open-source AI computer vision models to intelligently crop and select image subject matters contextually.
*   [ ] **Authentication System:** JWT-based user session handling, multi-tenant databases, and granular role architecture.
*   [ ] **Cloud Native Deployment:** Containerization utilizing Docker & orchestration definitions for AWS / Google Cloud Platforms via Kubernetes.
*   [ ] **Real-Time Client Preview:** WebSocket socket.io implementation for live-streaming partial rendering status to the client frontend.

---

## 👨‍💻 Author

**Piyush Ramteke**  
*Data Scientist & Full Stack Developer*  
Architecting fully tailored end-to-end data-science applications natively bound to premium SaaS interfaces.  
<a href="https://github.com/Piyu242005" target="_blank">
  <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Profile"/>
</a>

---

<div align="center">

*Distributed under the [MIT License](LICENSE).*
<br>
**Level up your content delivery today.**

</div>
