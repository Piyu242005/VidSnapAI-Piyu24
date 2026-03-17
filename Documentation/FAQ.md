#  Frequently Asked Questions

###  FFmpeg Error: subprocess.CalledProcessError...
**Reason**: FFmpeg is either not installed or strictly missing from your Global environment PATH array variables logically preventing pipeline execution states.
**Fix**: Install FFmpeg matching explicitly instructions laid out in [INSTALLATION.md](INSTALLATION.md). Validate running fmpeg -version cleanly through standard terminal maps.

###  TTS Failing or Voice Rendering Silence?
**Reason**: The string mapping the ELEVENLABS_API_KEY environmental variable has failed parsing missing variables or expired structures. 
**Fix**: Provide explicitly an active valid tracking map token dynamically inserting it back tracking ElevenLabs variable structures correctly initializing the 	ext_to_audio.py node headers.

###  Subtitles generating out of bounds?
**Reason**: Older FFmpeg versions occasionally fail padding variables pushing nodes awkwardly.
**Fix**: Ensure your FFmpeg version strictly hits > v6.0. Additionally, do not inject aspect-ratio requests pushing strictly beyond standard 1080x1920 mappings natively avoiding overflow tracking safely.

###  Whisper Audio fails loading Torch structures safely?
**Reason**: You are running native CPUs forcing complex mapping structures causing huge slowdowns dynamically loading.
**Fix**: Verify CUDA installation cleanly tracking 	orch.cuda.is_available(). It accurately detects hardware mapping safely bypassing errors.
