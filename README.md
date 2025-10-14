# 🛡️ ContentGuard

**ContentGuard** is an AI-powered NSFW image detection system that instantly analyzes and flags explicit content to help you protect your users and your brand.  
Built using **Flask** and a **state-of-the-art deep learning model**, it provides fast, reliable, and automated content moderation — ensuring a safer online environment for everyone.

---

## 🚀 Features

- ⚡ **Real-time Detection:** Instantly analyze uploaded images for NSFW or explicit content.  
- 🧠 **AI-Powered Model:** Uses a deep learning model trained on diverse datasets for high accuracy.  
- 🌐 **Flask Backend:** Lightweight and efficient Python backend for serving predictions.  
- 🧩 **Easy Integration:** Simple API endpoints for seamless integration into any web or mobile platform.  
- 🔒 **Privacy-Focused:** No data stored — all analysis happens securely on the server.

---

## 🏗️ Tech Stack

- **Backend:** Flask (Python)  
- **Model:** Deep Learning (NSFW image detection model)  
- **Frontend:** HTML, CSS, JavaScript  
- **Environment:** Python 3.10+  

---

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Prashray21/ContentGuard
   cd ContentGuard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask app:**
   ```bash
   python app.py
   ```

4. **Open your browser** and visit  
   👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## ⚙️ API Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| `POST` | `/analyze` | Upload an image and get NSFW prediction results |
| `GET`  | `/` | Returns the home page / upload interface |

Example Request:
```bash
curl -X POST -F "file=@example.jpg" http://127.0.0.1:5000/predict
```

Response:
```json
{
  "nsfw_score": 0.92,
  "safe": false
}
```

---

## 🧠 Model Details

The model is a fine-tuned CNN-based NSFW classifier trained on multiple open-source datasets for detecting:
- Pornographic content  
- Nudity  
- Suggestive material  
- Safe content  

The prediction score (`nsfw_score`) ranges between **0** (safe) and **1** (explicit).

---

## 🧑‍💻 Project Structure

```
ContentGuard/
│
├── app.py                  # Flask app entry point
├── style.css               # CSS file
├── script.js               # JS file
├── index.html              # HTML templates
├── nsfw_image_detection/   # Trained NSFW detection model
├── requirements.txt        # Dependencies
└── README.md               # Project documentation
```

---

## 📈 Future Improvements

- 🚀 Add video and GIF NSFW detection  
- 🤖 Integrate better multi-class labeling (e.g., hentai, suggestive, neutral)  
- ☁️ Deploy on cloud (Render / AWS / Hugging Face Spaces)  
- 🧩 Add authentication for API endpoints  

---

## 🛠️ Contributing

Pull requests are welcome!  
For major changes, please open an issue first to discuss what you’d like to change.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 💬 Acknowledgments

- [FalconsAI NSFW Detection Model](https://github.com/Falconsai/nsfw_image_detection)  
- [Flask](https://flask.palletsprojects.com/)  
- [TensorFlow](https://www.tensorflow.org/) / [PyTorch](https://pytorch.org/)

---

### ✨ Made with ❤️ by Our Team
