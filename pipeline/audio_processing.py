import os
import subprocess

def process_audio(voice_file, music_file, output_audio, max_duration=None):
    """
    Enhances audio, normalizes voiceover, and applies background music ducking.
    Adds slight fade in/out for professional sound.
    """
    if not os.path.exists(voice_file):
        raise FileNotFoundError(f"Voiceover track missing: {voice_file}")

    filters = []
    inputs = [f'-i "{voice_file}"']

    # Standardize voice channel, normalize loudness, add subtle compression
    filters.append("[0:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,acompressor=threshold=-15dB:ratio=4:attack=5:release=50[voice]")
    
    if music_file and os.path.exists(music_file):
        inputs.append(f'-i "{music_file}"')
        
        # Loop music, add ducking taking [voice] as sidechain
        # We also apply a subtle fade-in to the music to prevent harsh starts
        filters.append("[1:a]aloop=loop=-1:size=2e+09,volume=0.35,afade=t=in:st=0:d=2[music];"
                       "[music][0:a]sidechaincompress=threshold=-22dB:ratio=4.0:attack=10:release=200:makeup=1.5[bgm];"
                       "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2,volume=1.0[aout]")
        map_arg = "-map [aout]"
    else:
        filters.append("[0:a]volume=1.2[aout]")
        map_arg = "-map [aout]"

    filter_complex = ";".join(filters)
    
    # Clip duration if audio shouldn't exceed max length
    duration_flag = f"-t {max_duration}" if max_duration else ""

    command = f'ffmpeg -y {" ".join(inputs)} -filter_complex "{filter_complex}" {map_arg} {duration_flag} -c:a aac -b:a 256k "{output_audio}"'
    subprocess.run(command, shell=True, check=True, capture_output=True)
    
    return output_audio
