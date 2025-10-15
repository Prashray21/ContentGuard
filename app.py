from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import os
import cv2
import tempfile
import numpy as np

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

model_dir = "./nsfw_image_detection_model"

print("Loading NSFW detection model...")
if not os.path.exists(model_dir):
    print(f"Model not found in '{model_dir}'. Downloading from Hugging Face Hub...")
    try:
        processor = AutoImageProcessor.from_pretrained("Falconsai/nsfw_image_detection", use_fast=True)
        model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")
        print("Saving model to local cache...")
        processor.save_pretrained(model_dir)
        model.save_pretrained(model_dir)
        print("Model downloaded and saved successfully.")
    except Exception as e:
        print(f"Error downloading model: {e}")
        exit()
else:
    print(f"Loading model from local cache: '{model_dir}'")
    processor = AutoImageProcessor.from_pretrained(model_dir)
    model = AutoModelForImageClassification.from_pretrained(model_dir)
    print("Model loaded successfully.")

def analyze_single_image(image: Image.Image):
    """Analyzes a single PIL image and returns the label and confidence score."""
    try:
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            predicted_class_idx = logits.argmax(-1).item()
            label = model.config.id2label[predicted_class_idx]
            confidence = probs[0][predicted_class_idx].item() * 100
        return {"label": label, "confidence": round(confidence, 2)}
    except Exception as e:
        return {"error": f"Could not analyze the image. It might be corrupted. Details: {e}"}


def analyze_video(video_path, frame_sample_rate=2):
    """Analyzes a video by sampling frames and returns a verdict."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Could not open video file. It might be corrupted or in an unsupported format."}

    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    if frame_rate == 0:
        return {"error": "Invalid video with 0 FPS."}
        
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
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            result = analyze_single_image(image)
            if "label" in result and result["label"].lower() in ["nsfw", "porn", "sexual"]:
                nsfw_count += 1
        frame_count += 1
    cap.release()

    if total_analyzed == 0:
        return {"error": "No frames were analyzed. The video might be too short."}

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
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    filename = file.filename.lower()
    
    if any(filename.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"]):
        try:
            image = Image.open(file.stream).convert("RGB")
            result = analyze_single_image(image)
            if "error" in result:
                return jsonify(result), 500
            return jsonify({"type": "image", **result})
        except Exception as e:
            return jsonify({"error": f"Failed to process the image: {str(e)}"}), 500

    elif any(filename.endswith(ext) for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]):
        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                file.save(tmp.name)
                tmp_file_path = tmp.name
            
            result = analyze_video(tmp_file_path)
            if "error" in result:
                return jsonify(result), 500
            return jsonify({"type": "video", **result})
        except Exception as e:
            return jsonify({"error": f"Failed to process the video: {str(e)}"}), 500
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
    
    else:
        return jsonify({"error": "Unsupported file format. Please upload an image or video."}), 400

@app.route("/")
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    print("\n--- NSFW Detector Server is running ---")
    print("Access the web interface at: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
