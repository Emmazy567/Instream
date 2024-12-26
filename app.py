from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import threading
import os

app = Flask(__name__)

# Global variable to track progress and store the file path
progress = {"percent": 0, "file_path": None}

def download_video(url):
    """Function to download the video and track progress."""
    global progress

    def progress_hook(d):
        if d["status"] == "downloading":
            progress["percent"] = d.get("downloaded_bytes", 0) / d.get("total_bytes", 1) * 100
        elif d["status"] == "finished":
            progress["percent"] = 100
            progress["file_path"] = d["filename"]  # Save the file path

    ydl_opts = {
        "outtmpl": "downloads/%(title)s.%(ext)s",  # Save in downloads folder
        "progress_hooks": [progress_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    global progress
    progress["percent"] = 0
    progress["file_path"] = None  # Reset file path
    video_url = request.json.get("url")

    # Start the download in a separate thread
    threading.Thread(target=download_video, args=(video_url,)).start()

    return jsonify({"message": "Download started"})

@app.route("/progress", methods=["GET"])
def get_progress():
    return jsonify(progress)

@app.route("/get-file", methods=["GET"])
def get_file():
    """Endpoint to send the downloaded file to the user."""
    global progress

    if progress["file_path"] and os.path.exists(progress["file_path"]):
        return send_file(progress["file_path"], as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1080)  
