from flask import Flask, render_template, request, jsonify, send_file
import uuid
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from text_to_audio import text_to_speech_file as text_to_audio
from generate_process import create_reel

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
METADATA_FILE = 'reels_metadata.json'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Load metadata
def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def update_reel_stats(reel_id, stat_type='view'):
    metadata = load_metadata()
    if reel_id not in metadata:
        metadata[reel_id] = {
            'views': 0,
            'downloads': 0,
            'created_at': datetime.now().isoformat()
        }
    
    if stat_type == 'view':
        metadata[reel_id]['views'] = metadata[reel_id].get('views', 0) + 1
    elif stat_type == 'download':
        metadata[reel_id]['downloads'] = metadata[reel_id].get('downloads', 0) + 1
    
    save_metadata(metadata)
 

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    myid = uuid.uuid1()
    if request.method == "POST":
        print(request.files.keys())
        rec_id = request.form.get("uuid")
        desc = request.form.get("text")
        voice_id = request.form.get("voice_id", "pNInz6obpgDQGcFmaJgB")
        voice_speed = float(request.form.get("voice_speed", 1.0))
        music_file = request.form.get("music_file", "")
        music_volume = int(request.form.get("music_volume", 50))
        overlay_text = request.form.get("overlay_text", "")
        overlay_position = request.form.get("overlay_position", "bottom")
        overlay_color = request.form.get("overlay_color", "#ffffff")
        overlay_font = request.form.get("overlay_font", "Arial")
        overlay_size = int(request.form.get("overlay_size", 40))
        aspect_ratio = request.form.get("aspect_ratio", "9:16")
        quality = request.form.get("quality", "1080p")
        transition = request.form.get("transition", "none")
        
        input_files = []
        durations = {}
        
        if(not(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], rec_id)))):
            os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], rec_id))
        
        # Capture the description and save it to a file
        with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, "desc.txt"), "w") as f:
            f.write(desc)
        
        # Save settings
        settings = {
            'voice_id': voice_id,
            'voice_speed': voice_speed,
            'music_file': music_file,
            'music_volume': music_volume,
            'overlay_text': overlay_text,
            'overlay_position': overlay_position,
            'overlay_color': overlay_color,
            'overlay_font': overlay_font,
            'overlay_size': overlay_size,
            'aspect_ratio': aspect_ratio,
            'quality': quality,
            'transition': transition
        }
        
        with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, "settings.json"), "w") as f:
            json.dump(settings, f, indent=2)
        
        # Handle file uploads
        for key, value in request.files.items():
            if key.startswith('file') and value.filename:
                file = request.files[key]
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, filename))
                input_files.append(filename)
                
                # Get duration if provided
                duration_key = key.replace('file', 'duration')
                duration = float(request.form.get(duration_key, 1.0))
                durations[filename] = duration
        
        # Handle custom music upload
        custom_music = request.files.get('custom_music')
        if custom_music and custom_music.filename:
            music_filename = secure_filename(custom_music.filename)
            custom_music.save(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, music_filename))
            settings['music_file'] = music_filename
            settings['custom_music'] = True
        
        # Create input.txt with durations
        with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, "input.txt"), "w") as f:
            for fl in input_files:
                full_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, fl)).replace('\\', '/')
                duration = durations.get(fl, 1.0)
                f.write(f"file '{full_path}'\nduration {duration}\n")

        # Generate audio and reel synchronously
        try:
            # Import here to avoid circular imports
            from text_to_audio import text_to_speech_file
            text_to_speech_file(desc, rec_id, voice_id=voice_id, speed=voice_speed)
            create_reel(rec_id, settings=settings)
            
            
            # Save metadata
            metadata = load_metadata()
            metadata[rec_id] = {
                'views': 0,
                'downloads': 0,
                'created_at': datetime.now().isoformat(),
                'text': desc,
                'voice_id': voice_id,
                'music_file': settings.get('music_file', ''),
                'settings': settings
            }
            save_metadata(metadata)
            
            success = True
            reel_filename = f"{rec_id}.mp4"
        except Exception as e:
            print(f"Error generating reel: {e}")
            import traceback
            traceback.print_exc()
            success = False
            reel_filename = None
        return render_template("create.html", myid=myid, success=success, reel_filename=reel_filename)

    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    reels_dir = "static/reels"
    if not os.path.exists(reels_dir):
        os.makedirs(reels_dir)
        reels = []
    else:
        reels = [f for f in os.listdir(reels_dir) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    
    # Sort by creation date (newest first)
    metadata = load_metadata()
    reels.sort(key=lambda x: metadata.get(x.replace('.mp4', ''), {}).get('created_at', ''), reverse=True)
    
    print(f"Found {len(reels)} reels: {reels}")
    return render_template("gallery.html", reels=reels, metadata=metadata)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/api/preview-audio", methods=["POST"])
def preview_audio():
    try:
        data = request.json
        text = data.get('text', '')
        voice_id = data.get('voice_id', 'pNInz6obpgDQGcFmaJgB')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate temporary audio
        temp_id = str(uuid.uuid4())
        temp_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_{temp_id}')
        os.makedirs(temp_folder, exist_ok=True)
        
        try:
            from text_to_audio import text_to_speech_file
            text_to_speech_file(text, f'temp_{temp_id}', voice_id=voice_id, speed=1.0)
            audio_path = os.path.join(temp_folder, 'audio.mp3')
            
            if os.path.exists(audio_path):
                return send_file(audio_path, mimetype='audio/mpeg')
            else:
                return jsonify({'error': 'Failed to generate audio'}), 500
        finally:
            # Cleanup temp folder after a delay (or use background task)
            pass
            
    except Exception as e:
        print(f"Preview audio error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/share/<reel_id>")
def share_reel(reel_id):
    reel_filename = f"{reel_id}.mp4"
    reel_path = os.path.join("static/reels", reel_filename)
    
    if os.path.exists(reel_path):
        base_url = request.host_url.rstrip('/')
        share_url = f"{base_url}/static/reels/{reel_filename}"
        return jsonify({
            'share_url': share_url,
            'reel_id': reel_id,
            'filename': reel_filename
        })
    return jsonify({'error': 'Reel not found'}), 404

@app.route("/api/delete/<reel_id>", methods=["POST"])
def delete_reel(reel_id):
    try:
        reel_filename = f"{reel_id}.mp4"
        reel_path = os.path.join("static/reels", reel_filename)
        
        if os.path.exists(reel_path):
            os.remove(reel_path)
            
            # Remove from metadata
            metadata = load_metadata()
            if reel_id in metadata:
                del metadata[reel_id]
                save_metadata(metadata)
            
            # Remove upload folder
            upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], reel_id)
            if os.path.exists(upload_folder):
                import shutil
                shutil.rmtree(upload_folder)
            
            return jsonify({'success': True, 'message': 'Reel deleted successfully'})
        else:
            return jsonify({'error': 'Reel not found'}), 404
    except Exception as e:
        print(f"Delete error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/reel-stats/<reel_id>")
def reel_stats(reel_id):
    metadata = load_metadata()
    reel_data = metadata.get(reel_id, {})
    return jsonify({
        'views': reel_data.get('views', 0),
        'downloads': reel_data.get('downloads', 0),
        'created_at': reel_data.get('created_at', '')
    })

@app.route("/api/track-view/<reel_id>", methods=["POST"])
def track_view(reel_id):
    update_reel_stats(reel_id, 'view')
    return jsonify({'success': True})

@app.route("/api/track-download/<reel_id>", methods=["POST"])
def track_download(reel_id):
    update_reel_stats(reel_id, 'download')
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run(debug=True)