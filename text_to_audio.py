"""ElevenLabs speech generation with lazy provider initialization."""
import os
from pathlib import Path
from elevenlabs import VoiceSettings
from config import ELEVENLABS_API_KEY


def _client():
    api_key = os.getenv("ELEVENLABS_API_KEY") or ELEVENLABS_API_KEY
    if not api_key:
        raise RuntimeError("ElevenLabs is not configured")
    from elevenlabs.client import ElevenLabs
    return ElevenLabs(api_key=api_key, timeout=60.0, max_retries=2)


def text_to_speech_file(text: str, folder: str | None = None, voice_id: str = "pNInz6obpgDQGcFmaJgB", speed: float = 1.0, output_path: str | None = None) -> str:
    if not isinstance(text, str) or not text.strip() or len(text) > 500:
        raise ValueError("Text must contain 1 to 500 characters")
    if not 0.5 <= float(speed) <= 2.0:
        raise ValueError("Voice speed must be between 0.5 and 2.0")
    if output_path:
        target = Path(output_path)
    else:
        if not folder:
            raise ValueError("Provide folder or output_path")
        target = Path(os.getenv("UPLOAD_ROOT", "user_uploads")) / folder / "audio.mp3"
    target.parent.mkdir(parents=True, exist_ok=True)
    response = _client().text_to_speech.convert(
        voice_id=voice_id, output_format="mp3_22050_32", text=text,
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(stability=0.0, similarity_boost=1.0, style=0.0, use_speaker_boost=True, speed=float(speed)),
    )
    try:
        with target.open("wb") as stream:
            for chunk in response:
                if chunk:
                    stream.write(chunk)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError("Speech provider returned an empty audio file")
    return str(target)
