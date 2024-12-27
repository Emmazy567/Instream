from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import threading
import os
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Global variables
progress = {"percent": 0, "file_path": None}
scheduler = BackgroundScheduler()
scheduler.start()

# Directory to save downloads
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_video(url):
    """Function to download the video and track progress."""
    global progress

    def progress_hook(d):
        if d["status"] == "downloading":
            progress["percent"] = d.get("downloaded_bytes", 0) / d.get("total_bytes", 1) * 100
        elif d["status"] == "finished":
            progress["percent"] = 100
            progress["file_path"] = d["filename"]  # Save the file path
            schedule_file_deletion(d["filename"], 60)  # Schedule deletion after 1 hour

    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),  # Save in downloads folder
        "progress_hooks": [progress_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def schedule_file_deletion(filepath, delay):
    """Schedule a file to be deleted after a delay."""
    delete_time = datetime.now() + timedelta(seconds=delay)
    scheduler.add_job(delete_file, 'date', run_date=delete_time, args=[filepath])
    print(f"File {filepath} will be deleted at {delete_time}")

def delete_file(filepath):
    """Delete the specified file."""
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"Deleted file: {filepath}")

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
    app.run(debug=True)

