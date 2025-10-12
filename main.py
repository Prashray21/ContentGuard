import os
import torch
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from transformers import AutoImageProcessor, AutoModelForImageClassification

root = tk.Tk()
root.title("NSFW Image Detection")
root.geometry("390x480")
root.resizable(False, False)

selected_image_path = None
model = None
processor = None
image_label = None
result_label = None
confidence_label = None
progress_bar = None
status_label = None

def show_loading(text="Loading..."):
    global progress_bar, status_label
    if not progress_bar:
        progress_bar = ttk.Progressbar(root, mode="indeterminate", length=250)
        progress_bar.grid(row=4, column=0, columnspan=2, pady=10)
    if not status_label:
        status_label = tk.Label(root, text=text, font=("Arial", 11), fg="gray")
        status_label.grid(row=5, column=0, columnspan=2)
    else:
        status_label.config(text=text)
    progress_bar.start(10)
    root.update()

def hide_loading():
    global progress_bar, status_label
    if progress_bar:
        progress_bar.stop()
        progress_bar.grid_forget()
        progress_bar = None
    if status_label:
        status_label.grid_forget()
        status_label = None

def load_model():
    global model, processor
    model_dir = "./nsfw_image_detection_model"
    show_loading("Loading model...")
    if not os.path.exists(model_dir):
        processor = AutoImageProcessor.from_pretrained("Falconsai/nsfw_image_detection", use_fast=False)
        model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")
        processor.save_pretrained(model_dir)
        model.save_pretrained(model_dir)
    else:
        processor = AutoImageProcessor.from_pretrained(model_dir, use_fast=True)
        model = AutoModelForImageClassification.from_pretrained(model_dir)
    hide_loading()

def image_detection():
    global selected_image_path, model, processor, result_label, confidence_label
    if selected_image_path is None:
        if result_label:
            result_label.config(text="⚠️ Please select an image first!", fg="orange")
        return

    def detect():
        global confidence_label, result_label, model, processor, selected_image_path
        show_loading("Analyzing image...")
        if model is None or processor is None:
            load_model()
        image = Image.open(selected_image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
        predicted_class_idx = logits.argmax(-1).item()
        label = model.config.id2label[predicted_class_idx]
        confidence = probs[0][predicted_class_idx].item() * 100
        hide_loading()
        if result_label:
            result_label.config(text=f"Prediction: {label}", fg="green" if label.lower() == "safe" else "red")
        if confidence_label:
            confidence_label.config(text=f"Confidence: {confidence:.2f} %")
        else:
            confidence_label = tk.Label(root, text=f"Confidence: {confidence:.2f} %", font=("Arial", 11))
            confidence_label.grid(row=6, column=0, columnspan=2, pady=5)

    threading.Thread(target=detect).start()

def insert_image(filepath):
    global image_label, selected_image_path, result_label, confidence_label
    selected_image_path = filepath
    img = Image.open(filepath)
    img = img.resize((300, 300))
    tk_img = ImageTk.PhotoImage(img)
    if image_label:
        image_label.config(image=tk_img)
        image_label.image = tk_img
    else:
        image_label = tk.Label(root, image=tk_img)
        image_label.image = tk_img
        image_label.grid(row=2, column=0, columnspan=2, pady=10)
    if result_label:
        result_label.config(text="")
    else:
        result_label = tk.Label(root, text="", font=("Arial", 14))
        result_label.grid(row=3, column=0, columnspan=2, pady=5)
    if confidence_label:
        confidence_label.config(text="")

def get_path():
    filepath = filedialog.askopenfilename(
        title="Select a file",
        filetypes=(("Image Files", "*.jpg *.jpeg *.png"), ("All Files", "*.*"))
    )
    if filepath:
        insert_image(filepath)

sel_image_btn = tk.Button(root, text="Select Image", command=get_path, width=18, bg="#0078D7", fg="white", font=("Arial", 11))
sel_image_btn.grid(row=0, column=0, padx=10, pady=10)

det_image_btn = tk.Button(root, text="Detect Image", command=image_detection, width=18, bg="#28A745", fg="white", font=("Arial", 11))
det_image_btn.grid(row=0, column=1, padx=10, pady=10)

root.mainloop()