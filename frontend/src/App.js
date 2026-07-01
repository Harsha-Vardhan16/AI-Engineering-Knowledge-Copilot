// Backend URL
const BACKEND_URL = "http://127.0.0.1:8000";

// HTML Elements
const uploadForm = document.getElementById("uploadForm");
const pdfFile = document.getElementById("pdfFile");
const uploadStatus = document.getElementById("uploadStatus");

const askBtn = document.getElementById("askBtn");
const responseBox = document.getElementById("response");

// =========================
// Upload PDF
// =========================

uploadForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    if (pdfFile.files.length === 0) {

        uploadStatus.style.color = "red";
        uploadStatus.innerHTML = "Please choose a PDF file.";

        return;
    }

    const formData = new FormData();

    formData.append("file", pdfFile.files[0]);

    uploadStatus.style.color = "#ffffff";
    uploadStatus.innerHTML = "Uploading PDF...";

    try {

        const res = await fetch(`${BACKEND_URL}/upload`, {

            method: "POST",

            body: formData

        });

        const data = await res.json();

        uploadStatus.style.color = "#4ade80";

        uploadStatus.innerHTML = `
            ✅ Upload Successful <br><br>

            <b>Filename:</b> ${data.filename}<br>

            <b>Total Characters:</b> ${data.total_characters}<br>

            <b>Total Chunks:</b> ${data.total_chunks}
        `;

    }

    catch (error) {

        uploadStatus.style.color = "red";

        uploadStatus.innerHTML = "❌ Upload Failed.";

        console.error(error);

    }

});

// =========================
// Ask AI (Temporary)
// =========================

askBtn.addEventListener("click", function () {

    const question = document.getElementById("question").value;

    if (question.trim() === "") {

        responseBox.innerHTML = "Please enter a question.";

        return;
    }

    responseBox.innerHTML = `
    <b>Your Question:</b><br><br>
    ${question}
    <br><br>

    ⏳ AI Question Answering is coming in the next step.
    `;

});