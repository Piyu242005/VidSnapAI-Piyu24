Based on the project's setup, here is a step-by-step run guide tailored for your Windows machine.

### Prerequisites Check
Before running the application, make sure you have **FFmpeg** installed and added to your system's PATH. The app relies on it heavily for video processing. Also, your ElevenLabs API key is already configured in the `.env` file!

### Step 1: Initial Setup
You'll need to set up your virtual environment and install the required dependencies. Open a terminal (like PowerShell) and run the following commands:

```powershell
# Navigate to the project directory
cd c:\Users\Piyu\Downloads\VidSnapAI-Piyu24

# Set up the virtual environment (if you haven't already and the .venv directory is incomplete)
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\activate

# Install the necessary Python packages
pip install -r requirements.txt
```

### Step 2: Start the Web Server (Terminal 1)
Leave your first terminal open and running this command to start the main Flask API orchestrator:

```powershell
# Make sure your virtual environment is still activated
python main.py
```

### Step 3: Start the Background Worker (Terminal 2)
You need a second terminal to run the process that actually handles the background video generation:

1. Open a **new** terminal window or tab.
2. Run the following commands:

```powershell
# Navigate to the project folder again
cd c:\Users\Piyu\Downloads\VidSnapAI-Piyu24

# Activate the virtual environment in this new terminal
.\.venv\Scripts\activate

# Run the background worker
python generate_process.py
```

Once both scripts are running, you can open your web browser to the default Flask URL (typically `http://127.0.0.1:5000`) and the `VidSnapAI` dashboard will be ready to process requests!
