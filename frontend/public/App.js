// ===============================
// Backend URL
// ===============================

const BACKEND_URL = "http://127.0.0.1:8000";

// ===============================
// HTML Elements
// ===============================

const uploadForm = document.getElementById("uploadForm");
const pdfFile = document.getElementById("pdfFile");
const uploadStatus = document.getElementById("uploadStatus");

const askBtn = document.getElementById("askBtn");
const responseBox = document.getElementById("response");
const questionInput = document.getElementById("question");

console.log("App.js Loaded Successfully");

// ===============================
// Upload PDF
// ===============================

uploadForm.addEventListener("submit", async function (event) {
    

    
    

    console.log("Upload button clicked");

    event.preventDefault();

    if (pdfFile.files.length === 0) {

        uploadStatus.style.color = "red";
        uploadStatus.innerHTML = "Please choose a PDF.";

        return;
    }

    const formData = new FormData();
    formData.append("file", pdfFile.files[0]);

    uploadStatus.style.color = "white";
    uploadStatus.innerHTML = "Uploading PDF...";
    

    try {

        const response = await fetch(`${BACKEND_URL}/upload`, {
            
            method: "POST",
            body: formData
        });

        console.log("Status :", response.status);

        if (!response.ok) {

            const error = await response.text();

            uploadStatus.style.color = "red";
            uploadStatus.innerHTML = error;

            return;
        }

        const data = await response.json();

        console.log(data);

        uploadStatus.style.color = "lightgreen";

        uploadStatus.innerHTML = `
            <h3>✅ Upload Successful</h3>

            <b>Filename :</b> ${data.filename}<br><br>

            <b>Total Chunks :</b> ${data.chunks}<br><br>

            <b>${data.message}</b>
        `;

    }

    catch (err) {

        console.error(err);

        uploadStatus.style.color = "red";
        uploadStatus.innerHTML = "❌ Cannot connect to FastAPI Backend.";

    }

});

// ===============================
// Ask AI
// ===============================

askBtn.addEventListener("click", async function () {

    const question = questionInput.value.trim();

    if (question === "") {

        responseBox.innerHTML = "Please enter a question.";

        return;
    }

    responseBox.innerHTML = "Thinking...";

    try {

        const response = await fetch(
            `${BACKEND_URL}/search?question=${encodeURIComponent(question)}`
        );

        if (!response.ok) {

            responseBox.innerHTML = "Search failed.";

            return;
        }

        const data = await response.json();

        console.log(data);

        let answer = "";

        if (Array.isArray(data.answer)) {

            answer = data.answer.join("<br><br>");

        } else {

            answer = data.answer;

        }

        responseBox.innerHTML = `
            <h3>Your Question</h3>

            ${data.question}

            <hr>

            <h3>AI Answer</h3>

            ${answer}
        `;

    }

    catch (err) {

        console.error(err);

        responseBox.innerHTML = "❌ Cannot connect to FastAPI.";

    }

});