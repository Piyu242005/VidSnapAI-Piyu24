# VidSnapAI - AI-Powered TikTok/Reel Generator

VidSnapAI is an automated short-form video generation system that combines AI voice synthesis with programmatic video editing to create engaging TikTok and Instagram Reels content. This project was developed as part of a Bachelor's degree in Computer Applications at G H Raisoni University, Amravati.

## Overview

VidSnapAI streamlines content creation by:
- Converting text scripts into professional short-form videos
- Generating natural-sounding voiceovers using ElevenLabs AI
- Automating video assembly and editing via FFmpeg
- Providing a user-friendly web interface built with Flask

## Features

- **AI Voice Generation**: Utilizes ElevenLabs' text-to-speech technology for high-quality narration
- **Automated Video Processing**: FFmpeg-powered media processing pipeline
- **Web Interface**: Simple Flask-based UI for content input and video retrieval
- **Platform Optimized**: Outputs vertical format videos optimized for TikTok/Reels
- **Quick Turnaround**: Reduces manual editing time through automation

## System Requirements

### Software
- Python 3.x
- Flask web framework
- FFmpeg (version 4.0 or later)
- ElevenLabs API key
- Required Python packages (see requirements.txt)

### Hardware
- Multi-core CPU (quad-core or better recommended)
- Minimum 8GB RAM
- Internet connection for API access
- Compatible with Windows, Linux, or macOS

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/VidSnapAI.git
cd VidSnapAI
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Install FFmpeg
- Follow instructions at [ffmpeg.org](https://ffmpeg.org) for your operating system

5. Configure environment variables
```bash
export ELEVENLABS_API_KEY='your_api_key_here'
# On Windows: set ELEVENLABS_API_KEY=your_api_key_here
```

## Usage

1. Start the Flask server
```bash
flask run
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Enter your script or content in the web interface

4. Wait for processing to complete

5. Download your generated video

## System Architecture

The system consists of three main components:

1. **Web Interface (Flask)**
   - Handles user input
   - Manages file uploads
   - Delivers processed videos

2. **Voice Synthesis (ElevenLabs)**
   - Converts text to natural-sounding speech
   - Generates audio narration

3. **Video Processing (FFmpeg)**
   - Combines audio and visual elements
   - Applies transitions and effects
   - Ensures proper output format

## Future Improvements

- Multiple language support
- Expanded video template library
- Performance optimization
- Advanced editing features
- Platform integration options

## Technical Documentation

For detailed technical information, please refer to the following resources:
- [ElevenLabs Documentation](https://elevenlabs.io)
- [FFmpeg Documentation](https://ffmpeg.org)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Academic Context

This project was developed by Piyush Ramteke

## License

[Specify your chosen license]

## Contact

Piyush Ramteke  
piyu.143247@gmail.com

## Acknowledgments

- Mr.Piyush Ramteke (Project Guide)
- ElevenLabs for AI voice technology
- FFmpeg community for multimedia tools
