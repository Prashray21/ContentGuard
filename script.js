const toggleImage = document.querySelector(".toggle_image");
const toggleVideo = document.querySelector(".toggle_video");
const upload = document.getElementById("upload");
const upImage = document.querySelector(".up_image");
const upVideo = document.querySelector(".up_video");
const result = document.querySelector(".result");

let currentMode = "image";

toggleImage.addEventListener("click", () => {
    currentMode = "image";
    toggleImage.classList.add("toggle_image_active");
    toggleVideo.classList.remove("toggle_video_active");
    upload.accept = "image/*";
    result.innerHTML = "Upload an image for analysis.";
});

toggleVideo.addEventListener("click", () => {
    currentMode = "video";
    toggleVideo.classList.add("toggle_video_active");
    toggleImage.classList.remove("toggle_image_active");
    upload.accept = "video/*";
    result.innerHTML = "Upload a video for analysis.";
});

upload.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const fileURL = URL.createObjectURL(file);

    if (currentMode === "image") {
        upImage.src = fileURL;
        upImage.style.display = "block";
        upVideo.style.display = "none";
    } else {
        upVideo.src = fileURL;
        upVideo.style.display = "block";
        upImage.style.display = "none";
    }

    result.innerHTML = "⏳ Analyzing... Please wait.";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            result.innerHTML = "Error analyzing file.";
            return;
        }

        const data = await response.json();
        const { label, confidence } = data;

        result.innerHTML = `
            Prediction: <b>${label}</b><br>
            Confidence: ${confidence.toFixed(2)}%
        `;
        result.style.color = label.toLowerCase() === "normal" ? "green" : "red";

    } catch (error) {
        console.error("Error:", error);
        result.innerHTML = "Server not responding. Please try again.";
    }
});
document.querySelector('.menu_button').addEventListener('click', function() {
  document.querySelector('.menu_dropdown').classList.toggle('active');
});
