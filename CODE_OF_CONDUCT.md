# Code of Conduct: Project Setup and Execution Guide

This document serves as the primary guidance file on how to correctly set up, execute, and maintain the **VidSnapAI** project workplace. 

## 1. Prerequisites and Environment Setup

Before you can run the project, ensure you meet the system requirements:
- **Python:** You must have Python 3.8 or higher installed on your system.
- **FFmpeg:** FFmpeg is required for video compilation. Ensure it's installed and bound to your OS Path.
- **ElevenLabs API Key:** You need a valid API key for text-to-speech functionality. 

### Setting up the Virtual Environment
It is strictly recommended to operate within an isolated virtual environment to prevent dependency conflicts.
```bash
# Initialize virtual environment
python -m venv .venv

# Activate it (Windows)
.\.venv\Scripts\activate

# Activate it (Linux/MacOS)
source .venv/bin/activate
```

## 2. Installing Dependencies
With the active virtual environment, install the project dependencies:
```bash
pip install -r requirements.txt
```

## 3. Configuration
You must configure your local environment credentials before running the application. 
Open `config.py` in the project root directory and update it with your **ElevenLabs API Key**.

## 4. Running the Project
VidSnapAI requires two concurrent processes to function successfully: the web server and the background video processor.

### Step 1: Boot the Web Server
In your main terminal (with the virtual environment activated), start the Flask application:
```bash
python main.py
```
This will start the user interface and backend router.

### Step 2: Boot the Background Processor
Open a **new, separate terminal**, activate your virtual environment again, and run the asynchronous worker queue:
```bash
python generate_process.py
```
*Note: If the background processor is not running, requested videos will remain stuck in the queue and will not compile.*

## 5. Standard Operating Procedures
- Ensure both terminals are active during development or generation.
- Do not commit your personal `config.py` API keys to the repository.
- Uploaded media is temporarily staged in `user_uploads/` and processed assets are delivered to the frontend components.

By following this code of conduct and setup guide, you can ensure a stable environment for VidSnapAI.
