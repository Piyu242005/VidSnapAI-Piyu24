#  Usage Guide

Once installed, VidSnapAI relies on two background loops executing simultaneously. 

1. **Flask UI**: Captures files from users on port 5000.
2. **Reel Daemon**: Listens exclusively to the user_uploads/ folder and triggers backend render logic.

---

## 1. Starting the Application

You'll need two separate terminals. In your first terminal containing your activated virtual environment:
\\\ash
python main.py
\\\
*(This will begin broadcasting your interface locally on http://127.0.0.1:5000)*

In your second terminal:
\\\ash
python generate_process.py
\\\
*(This binds the directory listener).*

---

## 2. Generate a Reel

1. Head to http://127.0.0.1:5000/create.
2. **Text Request**: Provide a detailed description/script. (This will be synthesized fully by the Voice API and then timed cleanly by OpenAI Whisper).
3. **Uploads**: Drop any number of standard .png, .webp, or .jpg static images.
4. **Music Volume**: Decide your preference for background audio ducking logic.
5. Click **Generate**!

---

## 3. Explaining Output Paths

When generated, the pipeline orchestrates file saving structurally into a hashed folder. You will find:

- In user_uploads/{hash}/: 
  - udio.mp3 (the raw synthesized voice)
  - input.txt (a text map containing your raw image directories and specific durations)
  - Raw .jpg images

- **Final Export:**
  - Upon completion, the master encoded video is thrown directly into static/reels/ as .mp4.

*(This MP4 is now optimized strictly using -c:v libx264 -crf 18 -profile:v high resulting in absolute maximum quality natively accepted directly by TikTok & IG formatting standards).*
