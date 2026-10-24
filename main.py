from flask import Flask, render_template, request, jsonify, send_file
import uuid
from werkzeug.utils import secure_filename
import os
import json
import logging
import shutil
from pathlib import Path
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from security_utils import has_allowed_extension, is_valid_upload_id, parse_bounded_number

# Load environment variables
load_dotenv()

from text_to_audio import text_to_speech_file as text_to_audio
from generate_process import create_reel

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = str(BASE_DIR / "user_uploads")
REELS_FOLDER = BASE_DIR / "static" / "reels"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_MUSIC_EXTENSIONS = {"mp3", "wav", "m4a", "aac", "ogg"}
MAX_TEXT_LENGTH = 500
MAX_UPLOAD_BYTES = int(os.getenv("MAX_CONTENT_LENGTH", str(100 * 1024 * 1024)))
DEFAULT_VOICE_ID = "pNInz6obpgDQGcFmaJgB"
ALLOWED_ASPECT_RATIOS = {"9:16", "16:9", "1:1"}
ALLOWED_QUALITIES = {"720p", "1080p"}
ALLOWED_TRANSITIONS = {"none", "fade", "slide", "zoom"}

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("vidsnapai")



app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
app.config["MAX_FORM_MEMORY_SIZE"] = 2 * 1024 * 1024
app.config["MAX_FORM_PARTS"] = 200
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY") or os.urandom(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("COOKIE_SECURE", "0").lower() in {"1", "true", "yes"}
app.config["PREFERRED_URL_SCHEME"] = "https" if app.config["SESSION_COOKIE_SECURE"] else "http"
app.config["TRUSTED_HOSTS"] = [h.strip() for h in os.getenv("TRUSTED_HOSTS", "").split(",") if h.strip()] or None

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Validate critical environment variables
if not os.getenv("ELEVENLABS_API_KEY"):
    logger.warning("ELEVENLABS_API_KEY is not configured; voice generation will be unavailable.")

@app.after_request
def set_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if request.is_secure:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response

@app.errorhandler(413)
def request_too_large(_error):
    return jsonify({"error": "Upload too large. Reduce file size and try again."}), 413

@app.errorhandler(400)
def malformed_request(_error):
    return jsonify({"error": "Invalid request."}), 400

# Database Models
class Reel(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    text = db.Column(db.Text, nullable=True)
    voice_id = db.Column(db.String(50), nullable=True)
    music_file = db.Column(db.String(100), nullable=True)
    settings = db.Column(db.Text, nullable=True) # Stored as JSON string
    views = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'voice_id': self.voice_id,
            'music_file': self.music_file,
            'settings': json.loads(self.settings) if self.settings else {},
            'views': self.views,
            'downloads': self.downloads,
            'created_at': self.created_at.isoformat()
        }

# Create all tables on startup
with app.app_context():
    db.create_all()

# Helper for old metadata structure mapping
def update_reel_stats(reel_id, stat_type='view'):
    reel = Reel.query.get(reel_id)
    if reel:
        if stat_type == 'view':
            reel.views += 1
        elif stat_type == 'download':
            reel.downloads += 1
        db.session.commit()
 

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    myid = uuid.uuid4()
    if request.method == "POST":
        rec_id = (request.form.get("uuid") or "").strip()
        desc = (request.form.get("text") or "").strip()

        # Reject malformed identifiers and empty/oversized prompts before touching the filesystem.
        if not is_valid_upload_id(rec_id):
            return "Invalid generation ID.", 400
        if not desc or len(desc) > MAX_TEXT_LENGTH:
            return f"Text must contain 1 to {MAX_TEXT_LENGTH} characters.", 400
        try:
            voice_id = (request.form.get("voice_id") or DEFAULT_VOICE_ID).strip()
            voice_speed = parse_bounded_number(request.form.get("voice_speed", "1.0"), 0.5, 2.0, "voice speed")
            music_volume = int(parse_bounded_number(request.form.get("music_volume", "50"), 0, 100, "music volume"))
            overlay_size = int(parse_bounded_number(request.form.get("overlay_size", "40"), 20, 100, "overlay size"))
        except ValueError as exc:
            return str(exc), 400
        music_file = request.form.get("music_file", "").strip()
        overlay_text = (request.form.get("overlay_text") or "")[:300]
        overlay_position = request.form.get("overlay_position", "bottom")
        overlay_color = request.form.get("overlay_color", "#ffffff")
        overlay_font = request.form.get("overlay_font", "Arial")
        aspect_ratio = request.form.get("aspect_ratio", "9:16")
        quality = request.form.get("quality", "1080p")
        transition = request.form.get("transition", "none")
        if aspect_ratio not in ALLOWED_ASPECT_RATIOS or quality not in ALLOWED_QUALITIES or transition not in ALLOWED_TRANSITIONS:
            return "Invalid video export option.", 400
        if overlay_position not in {"top", "center", "bottom"} or overlay_font not in {"Arial", "Helvetica", "Times", "Courier"}:
            return "Invalid overlay option.", 400
        if not voice_id or len(voice_id) > 100:
            return "Invalid voice ID.", 400
        
        input_files = []
        durations = {}
        
        upload_dir = os.path.join(app.config["UPLOAD_FOLDER"], rec_id)
        os.makedirs(upload_dir, exist_ok=False)
        
        # Capture the description and save it to a file
        with open(os.path.join(upload_dir, "desc.txt"), "w", encoding="utf-8") as f:
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
        
        with open(os.path.join(upload_dir, "settings.json"), "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        
        # Handle file uploads
        for key, value in request.files.items():
            if key.startswith('file') and value.filename:
                file = request.files[key]
                if not has_allowed_extension(file.filename, ALLOWED_EXTENSIONS):
                    return "Unsupported image type. Use PNG or JPEG files.", 400
                filename = secure_filename(file.filename)
                if not filename:
                    return "Invalid upload filename.", 400
                if filename in {"desc.txt", "settings.json", "input.txt", "audio.mp3"}:
                    filename = f"image_{len(input_files) + 1}.{filename.rsplit('.', 1)[-1].lower()}"
                target = os.path.join(upload_dir, filename)
                file.save(target)
                if not _looks_like_image(target):
                    os.remove(target)
                    return "Uploaded file content is not a valid supported image.", 400
                input_files.append(filename)
                
                # Get duration if provided
                duration_key = key.replace('file', 'duration')
                try:
                    duration = parse_bounded_number(request.form.get(duration_key, "1.0"), 0.25, 30.0, "image duration")
                except ValueError as exc:
                    return str(exc), 400
                durations[filename] = duration
        
        # Handle custom music upload
        custom_music = request.files.get('custom_music')
        if custom_music and custom_music.filename:
            if not has_allowed_extension(custom_music.filename, ALLOWED_MUSIC_EXTENSIONS):
                return "Unsupported music type. Use MP3, WAV, M4A, AAC, or OGG.", 400
            music_filename = secure_filename(custom_music.filename)
            if not music_filename:
                return "Invalid music filename.", 400
            if music_filename in {"desc.txt", "settings.json", "input.txt", "audio.mp3"} or music_filename in input_files:
                music_filename = f"custom_music.{music_filename.rsplit('.', 1)[-1].lower()}"
            music_path = os.path.join(upload_dir, music_filename)
            custom_music.save(music_path)
            if not _looks_like_audio(music_path):
                os.remove(music_path)
                return "Uploaded file content is not a valid supported audio file.", 400
            settings['music_file'] = music_filename
            settings['custom_music'] = True
        
        # Create input.txt with durations
        with open(os.path.join(upload_dir, "input.txt"), "w", encoding="utf-8") as f:
            for fl in input_files:
                full_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, fl)).replace('\\', '/')
                duration = durations.get(fl, 1.0)
                f.write(f"file '{full_path.replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'\nduration {duration}\n")

        # Generate audio and reel synchronously
        try:
            # Import here to avoid circular imports
            from text_to_audio import text_to_speech_file
            text_to_speech_file(desc, rec_id, voice_id=voice_id, speed=voice_speed)
            create_reel(rec_id, settings=settings)
            
            # Save metadata to database
            new_reel = Reel(
                id=rec_id,
                text=desc,
                voice_id=voice_id,
                music_file=settings.get('music_file', ''),
                settings=json.dumps(settings)
            )
            db.session.add(new_reel)
            db.session.commit()
            
            success = True
            reel_filename = f"{rec_id}.mp4"
            error_message = None
        except Exception:
            logger.exception("Reel generation failed for request %s", rec_id)
            success = False
            reel_filename = None
            error_message = "Video generation failed. Check server logs and configuration, then try again."
        return render_template("create.html", myid=myid, success=success, reel_filename=reel_filename, error_message=error_message)

    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    reels_dir = str(REELS_FOLDER)
    if not os.path.exists(reels_dir):
        os.makedirs(reels_dir)
        reels = []
    else:
        reels = [f for f in os.listdir(reels_dir) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    
    # Query all reels from database, sort by creation date
    db_reels = Reel.query.order_by(Reel.created_at.desc()).all()
    metadata = {reel.id: reel.to_dict() for reel in db_reels}
    
    # Sort file list to match database order
    reels.sort(key=lambda x: metadata.get(x.replace('.mp4', ''), {}).get('created_at', ''), reverse=True)
    
    logger.info("Gallery loaded %d reel files", len(reels))
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
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"error": "Expected a JSON object."}), 400
        text = (data.get("text") or "").strip() if isinstance(data.get("text", ""), str) else ""
        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({'error': f'Text must be at most {MAX_TEXT_LENGTH} characters.'}), 400
        voice_id = (data.get("voice_id") or DEFAULT_VOICE_ID).strip() if isinstance(data.get("voice_id", DEFAULT_VOICE_ID), str) else DEFAULT_VOICE_ID
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate temporary audio
        temp_id = str(uuid.uuid4())
        temp_folder = os.path.join(app.config["UPLOAD_FOLDER"], f"temp_{temp_id}")
        os.makedirs(temp_folder, exist_ok=True)
        
        try:
            from text_to_audio import text_to_speech_file
            text_to_speech_file(text, f"temp_{temp_id}", voice_id=voice_id, speed=1.0)
            audio_path = os.path.join(temp_folder, "audio.mp3")
            if os.path.exists(audio_path):
                response = send_file(audio_path, mimetype="audio/mpeg")
                response.call_on_close(lambda: shutil.rmtree(temp_folder, ignore_errors=True))
                return response
            shutil.rmtree(temp_folder, ignore_errors=True)
            return jsonify({"error": "Audio file was not generated. Check server configuration."}), 500
                
        except Exception:
            logger.exception("Audio preview failed")
            shutil.rmtree(temp_folder, ignore_errors=True)
            return jsonify({"error": "Audio preview failed. Check server configuration and try again."}), 500
            
    except Exception:
        logger.exception("Unexpected audio preview error")
        return jsonify({"error": "Unable to process audio preview request."}), 500

@app.route("/api/share/<reel_id>")
def share_reel(reel_id):
    if not is_valid_upload_id(reel_id):
        return jsonify({"error": "Invalid reel ID"}), 400
    reel_filename = f"{reel_id}.mp4"
    reel_path = str(REELS_FOLDER / reel_filename)
    
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
        if not is_valid_upload_id(reel_id):
            return jsonify({"error": "Invalid reel ID"}), 400
        reel_filename = f"{reel_id}.mp4"
        reel_path = str(REELS_FOLDER / reel_filename)
        
        if os.path.exists(reel_path):
            os.remove(reel_path)
            
            # Remove from database
            reel = Reel.query.get(reel_id)
            if reel:
                db.session.delete(reel)
                db.session.commit()
            
            # Remove upload folder
            upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], reel_id)
            if os.path.exists(upload_folder):
                import shutil
                shutil.rmtree(upload_folder)
            
            return jsonify({'success': True, 'message': 'Reel deleted successfully'})
        else:
            return jsonify({'error': 'Reel not found'}), 404
    except Exception as e:
        logger.exception("Reel deletion failed")
        db.session.rollback()
        return jsonify({"error": "Unable to delete reel."}), 500

@app.route("/api/reel-stats/<reel_id>")
def reel_stats(reel_id):
    if not is_valid_upload_id(reel_id):
        return jsonify({"error": "Invalid reel ID"}), 400
    reel = Reel.query.get(reel_id)
    if reel:
        return jsonify({
            'views': reel.views,
            'downloads': reel.downloads,
            'created_at': reel.created_at.isoformat()
        })
    return jsonify({'views': 0, 'downloads': 0, 'created_at': ''})

@app.route("/api/track-view/<reel_id>", methods=["POST"])
def track_view(reel_id):
    if not is_valid_upload_id(reel_id):
        return jsonify({"error": "Invalid reel ID"}), 400
    update_reel_stats(reel_id, 'view')
    return jsonify({'success': True})

@app.route("/api/track-download/<reel_id>", methods=["POST"])
def track_download(reel_id):
    if not is_valid_upload_id(reel_id):
        return jsonify({"error": "Invalid reel ID"}), 400
    update_reel_stats(reel_id, 'download')
    return jsonify({'success': True})

def _looks_like_image(path):
    try:
        from PIL import Image
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False

def _looks_like_audio(path):
    # Signature checks reject obvious mislabeled files. Production deployments should also
    # decode media with a sandboxed ffprobe/FFmpeg process before processing it.
    try:
        with open(path, "rb") as media:
            header = media.read(16)
        return (
            header.startswith(b"ID3")
            or header.startswith(b"\xff\xfb")
            or header.startswith(b"\xff\xf3")
            or header.startswith(b"\xff\xf2")
            or header.startswith(b"RIFF")  # WAV
            or header.startswith(b"fLaC")
            or header.startswith(b"OggS")
            or (len(header) >= 8 and header[4:8] == b"ftyp")  # M4A/MP4 family
        )
    except OSError:
        return False

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    # Preserve Flask's HTTP exceptions and avoid leaking exception text or secrets.
    from werkzeug.exceptions import HTTPException
    if isinstance(error, HTTPException):
        return error
    logger.exception("Unhandled application exception")
    if request.path.startswith("/api/"):
        return jsonify({"error": "An unexpected server error occurred."}), 500
    return "An unexpected server error occurred.", 500

if __name__ == "__main__":
    debug_enabled = os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"}
    # Local development only. Use a production WSGI server behind HTTPS in deployment.
    app.run(host=os.getenv("FLASK_HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")), debug=debug_enabled)