from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import os
import cv2
import tempfile
import numpy as np

app = Flask(__name__)
CORS(app)

# Directory to cache model
model_dir = "./nsfw_image_detection_model"

# Load or download model
if not os.path.exists(model_dir):
    processor = AutoImageProcessor.from_pretrained("Falconsai/nsfw_image_detection", use_fast=True)
    model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")
    processor.save_pretrained(model_dir)
    model.save_pretrained(model_dir)
else:
    processor = AutoImageProcessor.from_pretrained(model_dir)
    model = AutoModelForImageClassification.from_pretrained(model_dir)


def analyze_single_image(image: Image.Image):
    """Analyze a single PIL image and return label/confidence."""
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=-1)
        predicted_class_idx = logits.argmax(-1).item()
        label = model.config.id2label[predicted_class_idx]
        confidence = probs[0][predicted_class_idx].item() * 100
    return {"label": label, "confidence": round(confidence, 2)}

def analyze_video(video_path, frame_sample_rate=2):
    """Analyze video by sampling frames every few seconds."""
    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(frame_rate * frame_sample_rate)
    frame_count = 0
    nsfw_count = 0
    total_analyzed = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            total_analyzed += 1
            # Convert frame to RGB PIL image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            result = analyze_single_image(image)
            if result["label"].lower() in ["nsfw", "porn", "sexual"]:
                nsfw_count += 1

        frame_count += 1

    cap.release()

    if total_analyzed == 0:
        return {"error": "No frames analyzed"}

    nsfw_ratio = (nsfw_count / total_analyzed) * 100
    return {
        "total_frames_analyzed": total_analyzed,
        "nsfw_frames": nsfw_count,
        "nsfw_ratio": round(nsfw_ratio, 2),
        "verdict": "NSFW" if nsfw_ratio > 10 else "SFW",
    }


@app.route("/analyze", methods=["POST"])
def analyze_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    # Detect file type
    filename = file.filename.lower()
    if any(filename.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"]):
        image = Image.open(file).convert("RGB")
        result = analyze_single_image(image)
        return jsonify({"type": "image", **result})

    elif any(filename.endswith(ext) for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            file.save(tmp.name)
            result = analyze_video(tmp.name)
        os.remove(tmp.name)
        return jsonify({"type": "video", **result})

    else:
        return jsonify({"error": "Unsupported file format"}), 400

if __name__ == "__main__":
     app.run(host='0.0.0.0', port=5000, debug=False)
