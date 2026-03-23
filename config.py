import os
from dotenv import load_dotenv

# Do not hardcode secrets
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# python generate_process.py
# #Run the generation script in the background to process any future uploads:
# python generate_process.py
# This will start the monitoring loop. Leave it running while the app is in use.