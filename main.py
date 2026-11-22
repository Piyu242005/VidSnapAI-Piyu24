from flask import Flask, render_template, request, jsonify, send_file, g, session, redirect, url_for
import uuid
from werkzeug.utils import secure_filename
import os
import json
import logging
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
from security_utils import has_allowed_extension, is_valid_upload_id, parse_bounded_number
from production.jobs import create_job_model, enqueue_job, init_jobs
from production.storage import storage_from_env, StorageConfigurationError

# Load environment variables before service configuration is read.
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
VERCEL_RUNTIME = os.getenv("VERCEL", "").lower() in {"1", "true"}
RUNTIME_DATA_DIR = Path("/tmp/vidsnapai") if VERCEL_RUNTIME else BASE_DIR
UPLOAD_FOLDER = str(RUNTIME_DATA_DIR / "user_uploads")
REELS_FOLDER = (RUNTIME_DATA_DIR / "reels") if VERCEL_RUNTIME else (BASE_DIR / "static" / "reels")
RUNTIME_DATA_DIR.mkdir(parents=True, exist_ok=True)
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
REELS_FOLDER.mkdir(parents=True, exist_ok=True)
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
if not os.getenv("FLASK_SECRET_KEY"):
    logger.warning("FLASK_SECRET_KEY is not set; sessions will not persist across restarts.")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("COOKIE_SECURE", "0").lower() in {"1", "true", "yes"}
app.config["PREFERRED_URL_SCHEME"] = "https" if app.config["SESSION_COOKIE_SECURE"] else "http"
app.config["TRUSTED_HOSTS"] = [h.strip() for h in os.getenv("TRUSTED_HOSTS", "").split(",") if h.strip()] or None

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
database_url = os.getenv("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    sqlite_path = (RUNTIME_DATA_DIR / "database.db") if VERCEL_RUNTIME else (Path(basedir) / "database.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(sqlite_path)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
init_jobs(db)
VideoJob = create_job_model(db)

# Validate critical environment variables
if not os.getenv("ELEVENLABS_API_KEY"):
    logger.warning("ELEVENLABS_API_KEY is not configured; voice generation will be unavailable.")

@app.before_request
def reject_mutating_requests_without_same_origin():
    # Origin checking is a defense-in-depth CSRF guard for browser form/API mutations.
    # Deployments using a reverse proxy must configure the expected public host.
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return None
    origin = request.headers.get("Origin")
    if not origin:
        return None  # Non-browser clients may omit Origin; authentication is still required for public deployment.
    from urllib.parse import urlparse
    parsed = urlparse(origin)
    if parsed.scheme not in {"http", "https"} or parsed.netloc != request.host:
        return jsonify({"error": "Cross-origin request rejected."}), 403
    return None

@app.after_request
def set_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if request.is_secure:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response

@app.errorhandler(CSRFError)
def csrf_error(_error):
    return jsonify({"error": "The form token is missing or expired. Refresh the page and retry."}), 400

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


class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    quota_date = db.Column(db.Date, nullable=True)
    daily_jobs = db.Column(db.Integer, nullable=False, default=0)
    minute_window = db.Column(db.DateTime(timezone=True), nullable=True)
    minute_jobs = db.Column(db.Integer, nullable=False, default=0)

with app.app_context():
    db.create_all()

# Schema changes are applied by a controlled migration command, not app import.

# Helper for old metadata structure mapping
def update_reel_stats(reel_id, stat_type='view'):
    reel = Reel.query.get(reel_id)
    if reel:
        if stat_type == 'view':
            reel.views += 1
        elif stat_type == 'download':
            reel.downloads += 1
        db.session.commit()


def _auth_value(field):
    payload = request.get_json(silent=True) if request.is_json else None
    value = payload.get(field) if isinstance(payload, dict) else request.form.get(field)
    return value.strip() if isinstance(value, str) else ""


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth.html", mode="register")
    email = _auth_value("email").lower()
    password = _auth_value("password")
    if not email or "@" not in email or len(email) > 255:
        return jsonify({"error": "invalid_email"}), 400
    if len(password) < 8 or len(password) > 128:
        return jsonify({"error": "invalid_password"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email_exists"}), 409
    user = User(email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    session.clear()
    session["user_id"] = user.id
    if not request.is_json:
        return redirect(url_for("create"))
    return jsonify({"user_id": user.id, "email": user.email}), 201


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth.html", mode="login")
    email = _auth_value("email").lower()
    password = _auth_value("password")
    user = User.query.filter_by(email=email).first() if email else None
    if not user or not user.is_active or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid_credentials"}), 401
    session.clear()
    session["user_id"] = user.id
    if not request.is_json:
        return redirect(url_for("create"))
    return jsonify({"user_id": user.id, "email": user.email}), 200


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    if not request.is_json:
        return redirect(url_for("home"))
    return jsonify({"success": True}), 200


def _check_job_quota(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user or not user.is_active:
        return "authentication_required", 401
    today = datetime.now(timezone.utc).date()
    now = datetime.now(timezone.utc)
    if user.quota_date != today:
        user.quota_date = today
        user.daily_jobs = 0
    minute_window = user.minute_window
    if minute_window is not None and minute_window.tzinfo is None:
        minute_window = minute_window.replace(tzinfo=timezone.utc)
    if minute_window is None or (now - minute_window).total_seconds() >= 60:
        user.minute_window = now
        user.minute_jobs = 0
    try:
        daily_limit = max(0, int(os.getenv("DAILY_JOB_LIMIT", "20")))
        minute_limit = max(0, int(os.getenv("JOB_CREATION_RATE_LIMIT", "5")))
    except ValueError:
        daily_limit, minute_limit = 20, 5
    if user.daily_jobs >= daily_limit:
        db.session.rollback()
        return "quota_exceeded", 429
    if user.minute_jobs >= minute_limit:
        db.session.rollback()
        return "rate_limit_exceeded", 429
    user.daily_jobs += 1
    user.minute_jobs += 1
    db.session.commit()
    return None, 200

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    myid = uuid.uuid4()
    if request.method == "GET":
        return render_template("create.html", myid=myid)
    if not _request_user_id():
        if request.accept_mimetypes.best == "application/json":
            return jsonify({"error": "authentication_required"}), 401
        return render_template("create.html", myid=myid, success=False,
            error_message="Sign in before creating a reel."), 401
    if VERCEL_RUNTIME:
        # Keep the current UI closed until authenticated async processing is configured.
        return render_template("create.html", myid=myid, success=False,
            error_message="Online generation is not enabled until authentication, PostgreSQL, object storage and the persistent worker are configured."), 503
    try:
        return _create_local_reel(myid)
    except Exception:
        logger.exception("Unhandled local reel submission error")
        if request.accept_mimetypes.best == "application/json":
            return jsonify({"error": "job_submission_failed"}), 500
        return render_template("create.html", myid=myid, success=False,
            error_message="Job submission failed. Please try again."), 500


def _request_user_id():
    """Use a server-established identity; never trust user_id from request JSON."""
    user_id = getattr(g, "user_id", None) or session.get("user_id")
    return str(user_id) if user_id else None


@app.route("/api/v1/jobs", methods=["POST"])
def create_job_api():
    """Create an async job, protected by authentication and strict manifest validation."""
    user_id = _request_user_id()
    if not user_id:
        return jsonify({"error": "authentication_required"}), 401
    quota_error, quota_status = _check_job_quota(user_id)
    if quota_error:
        return jsonify({"error": quota_error}), quota_status
    if not request.is_json:
        return jsonify({"error": "expected_json"}), 415
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_request"}), 400
    manifest = payload.get("manifest")
    if not isinstance(manifest, dict):
        return jsonify({"error": "invalid_manifest"}), 400
    text = manifest.get("text")
    inputs = manifest.get("inputs")
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT_LENGTH:
        return jsonify({"error": "invalid_text"}), 400
    if not isinstance(inputs, list) or not inputs or len(inputs) > 30:
        return jsonify({"error": "invalid_inputs"}), 400
    for entry in inputs:
        if not isinstance(entry, dict) or not isinstance(entry.get("key"), str):
            return jsonify({"error": "invalid_input_manifest"}), 400
        key = entry["key"]
        if key.startswith("/") or "\\" in key or ".." in key.split("/"):
            return jsonify({"error": "invalid_input_key"}), 400
    idem = request.headers.get("Idempotency-Key", "")
    if len(idem) > 128:
        return jsonify({"error": "invalid_idempotency_key"}), 400
    try:
        job, created = enqueue_job(VideoJob, user_id, manifest, idem or None)
        return jsonify({"job_id": job.id, "status": job.status}), (202 if created else 200)
    except Exception:
        db.session.rollback()
        logger.exception("Job submission failed")
        return jsonify({"error": "job_submission_failed"}), 500


@app.route("/api/v1/jobs/<job_id>", methods=["GET"])
def get_job_api(job_id):
    user_id = _request_user_id()
    if not user_id:
        return jsonify({"error": "authentication_required"}), 401
    job = VideoJob.query.filter_by(id=job_id, user_id=user_id).first()
    if not job:
        return jsonify({"error": "job_not_found"}), 404
    return jsonify(job.public_dict())


@app.route("/api/v1/jobs/<job_id>/download", methods=["GET"])
def download_job_api(job_id):
    user_id = _request_user_id()
    if not user_id:
        return jsonify({"error": "authentication_required"}), 401
    job = VideoJob.query.filter_by(id=job_id, user_id=user_id).first()
    if not job:
        return jsonify({"error": "job_not_found"}), 404
    if job.status != "succeeded" or not job.output_key:
        return jsonify({"error": "job_not_complete"}), 409
    try:
        storage = storage_from_env()
        if not hasattr(storage, "presign_download"):
            return jsonify({"error": "signed_download_unavailable"}), 503
        return jsonify({"download_url": storage.presign_download(job.output_key, 180), "expires_in": 180})
    except StorageConfigurationError:
        return jsonify({"error": "storage_not_configured"}), 503


def _create_local_reel(myid):
    """Async-only local create flow; generation is performed exclusively by worker.py."""
    user_id = _request_user_id()
    if not user_id:
        return jsonify({"error": "authentication_required"}), 401

    rec_id = (request.form.get("uuid") or "").strip()
    desc = (request.form.get("text") or "").strip()
    if not is_valid_upload_id(rec_id):
        return "Invalid generation ID.", 400
    if not desc or len(desc) > MAX_TEXT_LENGTH:
        return f"Text must contain 1 to {MAX_TEXT_LENGTH} characters.", 400

    quota_error, quota_status = _check_job_quota(user_id)
    if quota_error:
        return jsonify({"error": quota_error}), quota_status

    try:
        storage = storage_from_env()
    except StorageConfigurationError:
        return jsonify({"error": "storage_not_configured"}), 503

    try:
        voice_id = (request.form.get("voice_id") or DEFAULT_VOICE_ID).strip()
        voice_speed = parse_bounded_number(request.form.get("voice_speed", "1.0"), 0.5, 2.0, "voice speed")
        overlay_size = int(parse_bounded_number(request.form.get("overlay_size", "40"), 20, 100, "overlay size"))
    except ValueError as exc:
        return str(exc), 400

    aspect_ratio = request.form.get("aspect_ratio", "9:16")
    quality = request.form.get("quality", "1080p")
    transition = request.form.get("transition", "none")
    if aspect_ratio not in ALLOWED_ASPECT_RATIOS or quality not in ALLOWED_QUALITIES or transition not in ALLOWED_TRANSITIONS:
        return "Invalid video export option.", 400

    inputs = []
    for key, upload in request.files.items():
        if not key.startswith("file") or not upload.filename:
            continue
        if not has_allowed_extension(upload.filename, ALLOWED_EXTENSIONS):
            return "Unsupported image type. Use PNG or JPEG files.", 400
        filename = secure_filename(upload.filename)
        if not filename:
            return "Invalid upload filename.", 400
        suffix = Path(filename).suffix.lower()
        with tempfile.TemporaryDirectory(prefix="vidsnapai-upload-") as temp_dir:
            temp_path = Path(temp_dir) / ("image" + suffix)
            upload.save(temp_path)
            if not _looks_like_image(str(temp_path)):
                return "Uploaded file content is not a valid supported image.", 400
            storage_key = f"inputs/{user_id}/{rec_id}/{len(inputs):02d}{suffix}"
            storage.put_file(storage_key, str(temp_path))
        duration_key = key.replace("file", "duration")
        try:
            duration = parse_bounded_number(request.form.get(duration_key, "1.0"), 0.25, 30.0, "image duration")
        except ValueError as exc:
            return str(exc), 400
        inputs.append({"key": storage_key, "filename": filename, "duration": duration})

    if not inputs:
        return "At least one image is required.", 400

    settings = {
        "voice_id": voice_id,
        "voice_speed": voice_speed,
        "music_volume": int(parse_bounded_number(request.form.get("music_volume", "50"), 0, 100, "music volume")),
        "overlay_text": (request.form.get("overlay_text") or "")[:300],
        "overlay_position": request.form.get("overlay_position", "bottom"),
        "overlay_color": request.form.get("overlay_color", "#ffffff"),
        "overlay_font": request.form.get("overlay_font", "Arial"),
        "overlay_size": overlay_size,
        "aspect_ratio": aspect_ratio,
        "quality": quality,
        "transition": transition,
    }
    try:
        job, _ = enqueue_job(VideoJob, user_id,
            {"text": desc, "inputs": inputs, "settings": settings})
    except Exception:
        db.session.rollback()
        logger.exception("Failed to enqueue local create job")
        return jsonify({"error": "job_submission_failed"}), 500
    return jsonify({"job_id": job.id, "status": job.status}), 202
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
    if not _request_user_id():
        return jsonify({"error": "authentication_required"}), 401
    if VERCEL_RUNTIME:
        return jsonify({"error": "Audio preview requires the separate media worker and is disabled on Vercel serverless."}), 503
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
    if not _request_user_id():
        return jsonify({"error": "authentication_required"}), 401
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
    except Exception:
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
