import os
import hashlib
import json
from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'

# Load known malware hashes
with open("malware_hashes.json", "r") as file:
    MALWARE_HASHES = json.load(file)

# Function to calculate SHA256 hash
def calculate_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if file was uploaded
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No file selected")
            return redirect(request.url)
        
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        # Calculate file hash
        file_hash = calculate_hash(file_path)
        
        # Check if it's malware
        is_malware = file_hash in MALWARE_HASHES
        
        # Clean up uploaded file
        os.remove(file_path)

        return render_template("result.html", file_hash=file_hash, is_malware=is_malware)

    return render_template("index.html")

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
