from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import os

app = Flask(__name__)
CORS(app)  # <-- ADD THIS LINE

model_dir = "./nsfw_image_detection_model"

# Load model
if not os.path.exists(model_dir):
    processor = AutoImageProcessor.from_pretrained("Falconsai/nsfw_image_detection")
    model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")
    processor.save_pretrained(model_dir)
    model.save_pretrained(model_dir)
else:
    processor = AutoImageProcessor.from_pretrained(model_dir)
    model = AutoModelForImageClassification.from_pretrained(model_dir)

@app.route("/analyze", methods=["POST"])
def analyze_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    image = Image.open(file).convert("RGB")

    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=-1)
        predicted_class_idx = logits.argmax(-1).item()
        label = model.config.id2label[predicted_class_idx]
        confidence = probs[0][predicted_class_idx].item() * 100

    return jsonify({"label": label, "confidence": round(confidence, 2)})

if __name__ == "__main__":
    app.run(debug=True)