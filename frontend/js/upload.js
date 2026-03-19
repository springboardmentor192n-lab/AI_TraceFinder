async function upload() {

    let files = document.getElementById("fileInput").files

    if (files.length === 0) {
        alert("Please select images")
        return
    }

    let resultsDiv = document.getElementById("results")

    resultsDiv.innerHTML = "<h3>🔍 AI Analyzing documents...</h3>"

    for (let i = 0; i < files.length; i++) {

        let file = files[i]

        let formData = new FormData()
        formData.append("file", file)

        let response = await fetch("https://ai-tracefinder.onrender.com", {
            method: "POST",
            body: formData
        })

        let data = await response.json()

        let card = document.createElement("div")
        card.className = "result-card"

        let reader = new FileReader()

        reader.onload = function(e) {

            let status = ""
            let statusClass = ""

            if (data.confidence >= 85) {
                status = "Authentic Document"
                statusClass = "status-good"
            } else {
                status = "Possible Tampering"
                statusClass = "status-warning"
            }

            card.innerHTML = `
        <img src="${e.target.result}" width="120"><br>

        <b>File:</b> ${file.name}<br>
        Scanner: ${data.scanner}<br>

        <div class="${statusClass}">
        ${status}
        </div>

        Confidence:
        <div class="progress-bar">
        <div class="progress" style="width:${data.confidence}%">
        ${data.confidence}%
        </div>
        </div>

        <br>
        <button onclick="downloadReport('${file.name}','${data.scanner}','${data.confidence}','${status}')">
        Download Report
        </button>
        `
        }

        reader.readAsDataURL(file)

        resultsDiv.appendChild(card)

    }

}

function downloadReport(filename, scanner, confidence, status) {

    const { jsPDF } = window.jspdf

    let doc = new jsPDF()

    doc.setFontSize(18)
    doc.text("TraceFinder Forensic Analysis Report", 20, 20)

    doc.setFontSize(12)

    doc.text("File Name: " + filename, 20, 40)
    doc.text("Detected Scanner: " + scanner, 20, 50)
    doc.text("Confidence Score: " + confidence + "%", 20, 60)
    doc.text("Document Status: " + status, 20, 70)

    doc.text("Analysis Engine: TraceFinder AI Scanner Detection", 20, 90)

    doc.save("TraceFinder_Report_" + filename + ".pdf")

}