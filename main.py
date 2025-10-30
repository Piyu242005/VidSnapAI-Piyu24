from flask import Flask, render_template, request
import uuid
from werkzeug.utils import secure_filename
import os
from text_to_audio import text_to_speech_file as text_to_audio
from generate_process import create_reel

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 

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
        input_files = []
        if(not(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], rec_id)))):
            os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], rec_id))
        # Capture the description and save it to a file
        with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, "desc.txt"), "w") as f:
            f.write(desc)
        for key, value in request.files.items():
            print(key, value)
            # Upload the file
            file = request.files[key]
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], rec_id,  filename))
                input_files.append(filename)
                print(filename)
        for fl in input_files:
            # Use absolute path for ffmpeg compatibility
            full_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, fl)).replace('\\', '/')
            with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id,  "input.txt"), "a") as f:
                f.write(f"file '{full_path}'\nduration 1\n")

        # Generate audio and reel synchronously
        try:
            text_to_audio(desc, rec_id)
            create_reel(rec_id)
            with open("done.txt", "a") as f:
                f.write(rec_id + "\n")
            success = True
            reel_filename = f"{rec_id}.mp4"
        except Exception as e:
            print(f"Error generating reel: {e}")
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
    print(f"Found {len(reels)} reels: {reels}")
    return render_template("gallery.html", reels=reels)

app.run(debug=True)