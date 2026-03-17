#  Installation Guide

This completely specifies the correct method to set up **VidSnapAI** across your local environment efficiently.

## Prerequisites
Before beginning, ensure you have the following installed on your machine:
* Python 3.8+
* git
* **FFmpeg** (crucial for video capabilities)

---

## 1. FFmpeg Configuration

VidSnapAI utilizes the Python \subprocess\ module to send massive filter commands directly natively through FFmpeg for immense speed. **FFmpeg must be recognizable in your environmental PATH variables.**

* **Windows:**
  1. Download the [FFmpeg essentials package](https://www.gyan.dev/ffmpeg/builds/)
  2. Extract it to \C:\ffmpeg\
  3. Add \C:\ffmpeg\bin\ to your System Environment variables under \PATH\.
* **Mac/Linux:**
  \\\ash
  brew install ffmpeg       # MacOS
  sudo apt install ffmpeg   # Linux/Ubuntu
  \\\

---

## 2. Setting up the Repository

Clone the project down to a safe, workable directory space.

\\\ash
git clone https://github.com/yourusername/VidSnapAI.git
cd VidSnapAI
\\\

Next, initialize a Python Virtual Environment to keep the specific models isolated safely.

**Windows:**
\\\ash
python -m venv .venv
.venv\Scripts\activate
\\\

**Mac/Linux:**
\\\ash
python -m venv .venv
source .venv/bin/activate
\\\

---

## 3. Install Python Dependencies

Run PIP to install the core components supporting both Flask and our Machine Learning stack (Whisper/Torch/Librosa).

\\\ash
pip install -r requirements.txt
\\\

*(Note: During runtime, Whisper dynamically checks for \cuda\ to route computations through your GPU automatically).*

---

## 4. Environment Keys & TTS

If using **ElevenLabs** for synthesized speech, you must update \	ext_to_audio.py\ to use your valid API key string.

\\\python
# Place into text_to_audio.py logic OR export locally:
export ELEVENLABS_API_KEY="your-api-key-here"
\\\

---
*Ready to jump in? Return to the [Usage Document](USAGE.md) to kickstart your first reel.*
