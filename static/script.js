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
    resetUI("Upload an image for analysis.");
});

toggleVideo.addEventListener("click", () => {
    currentMode = "video";
    toggleVideo.classList.add("toggle_video_active");
    toggleImage.classList.remove("toggle_image_active");
    upload.accept = "video/*";
    resetUI("Upload a video for analysis.");
});

function resetUI(message) {
    upImage.style.display = "none";
    upVideo.style.display = "none";
    upImage.src = "";
    upVideo.src = "";
    result.style.display = "block";
    result.innerHTML = message;
    result.style.color = 'rgb(107, 114, 128)';
}

upload.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    result.style.display = "none";
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

    const tempResultContainer = document.createElement('div');
    tempResultContainer.className = 'result text-black-500 text-center';
    tempResultContainer.innerHTML = "⏳ Analyzing... Please wait.";
    upImage.parentElement.appendChild(tempResultContainer);
    
    result.style.display = "none";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") !== -1) {
                const errorData = await response.json();
                throw new Error(errorData.error || "An unknown server error occurred.");
            } else {
                throw new Error(`Server returned an unexpected response. Status: ${response.status}`);
            }
        }

        const data = await response.json();
        
        result.style.display = 'block';

        if (data.type === "image") {
            const { label, confidence } = data;
            result.innerHTML = `
                <b class='text-lg'>Image Analysis Result</b><br>
                Prediction: <b class='font-semibold'>${label}</b><br>
                Confidence: ${confidence.toFixed(2)}%
            `;
            result.style.color = label.toLowerCase() === "normal" || label.toLowerCase() === "sfw" ? "green" : "red";
        } else if (data.type === "video") {
            const { total_frames_analyzed, nsfw_frames, nsfw_ratio, verdict } = data;
            const prediction = verdict.toLowerCase() === "nsfw" ? "Not Safe For Work!" : "Safe For Work!";
            result.innerHTML = `
                <b class='text-lg'>Video Analysis Result</b><br>
                Frames Analyzed: ${total_frames_analyzed}<br>
                NSFW Frames: ${nsfw_frames}<br>
                NSFW Ratio: ${nsfw_ratio}%<br>
                Verdict: <b class='font-semibold'>${prediction}</b>
            `;
            result.style.color = verdict === "SFW" ? "green" : "red";
        } else if (data.error) {
             throw new Error(data.error);
        }

    } catch (error) {
        console.error("Error:", error);
        result.style.display = 'block';
        result.innerHTML = `Error: ${error.message}`;
        result.style.color = "orange";
    } finally {
        // upImage.style.display = "none";
        // upVideo.style.display = "none";
        if (tempResultContainer) {
            tempResultContainer.remove();
        }
    }
});

