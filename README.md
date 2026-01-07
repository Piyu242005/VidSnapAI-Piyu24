# VidSnapAI - AI-Powered Video Reel Generator

VidSnapAI is an advanced web application that automates the creation of short-form video content (Reels/TikToks). By combining AI-powered voice synthesis (ElevenLabs) covering FFmpeg for video processing, it transforms simple text scripts into professional-quality video reels.

Recent updates include a modernized UI with a **theme toggle system** (Red/Black Dark Mode & Warm Beige Light Mode), a redesigned **About** page featuring pixel-perfect team cards, and significant code cleanup.

![Project Preview](static/Piyu24.jpg)

## 🚀 Key Features

- **AI Voice Synthesis**: Integrated with ElevenLabs API for realistic voiceovers.
- **Automated Video Editing**: Programmatic video assembly using FFmpeg (transitions, overlays, audio mixing).
- **Theme Toggle System**:
    - **Dark Mode**: Signature Red & Black aesthetic.
    - **Light Mode**: New Warm Beige theme (`#fdfcfb` → `#e2d1c3`).
    - *Persists user preference via LocalStorage.*
- **Modern UI/UX**:
    - Responsive design with glassmorphism effects.
    - Revamped **About** page with a high-fidelity "Meet our team" section.
    - Interactive "Create Reel" workflow.
- **Platform Optimized**: Outputs vertical 9:16 video format perfect for social media.

## 📂 Project Structure

```
VidSnapAI-Piyu24/
├── main.py                 # Core Flask application entry point
├── generate_process.py     # Video generation logic (FFmpeg + Audio mixing)
├── text_to_audio.py        # ElevenLabs text-to-speech integration
├── config.py               # Configuration settings
├── requirements.txt        # Project dependencies
├── static/                 # Static assets
│   ├── css/                # Stylesheets (style.css, about.css, etc.)
│   ├── js/                 # JavaScript (theme.js, notifications.js)
│   ├── fonts/              # Local fonts
│   └── ...                 # Uploaded/Generated media placeholders
├── templates/              # HTML Templates (Jinja2)
│   ├── base.html           # Base layout with Navbar/Footer
│   ├── index.html          # Homepage
│   ├── create.html         # Video creation form
│   ├── about.html          # Team & Mission page
│   └── ...
└── user_uploads/           # Directory for user-uploaded content
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- [FFmpeg](https://ffmpeg.org/download.html) installed and added to system PATH.
- An [ElevenLabs API Key](https://elevenlabs.io/).

### Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/VidSnapAI.git
   cd VidSnapAI
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   - Ensure FFmpeg is accessible.
   - Set up your ElevenLabs API key in the application or environment variables.

5. **Run the Application**
   ```bash
   python main.py
   ```
   Access the app at `http://localhost:5000`.

## 🎨 UI & Theming

The application now supports dynamic theming:
- **Toggle** the theme using the icon in the navbar.
- **Dark Mode**: Deep blacks with vibrant red accents (`#ff0000`).
- **Light Mode**: Soft warm beige gradients (`#fdfcfb` to `#e2d1c3`) with dark brown text.

## 👥 Team

**Piyush Ramteke**  
*Data Scientist & Full Stack Developer*  
Focused on scalable web applications and AI-driven solutions.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
Developed by **Piyush Ramteke**
