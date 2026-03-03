function createPanel() {
    const panel = document.createElement("div");
    panel.id = "lecturelens-panel";

    panel.innerHTML = `
        <h2>LectureLens AI</h2>
        <input type="text" id="ll-query" placeholder="Ask about this video..." />
        <button id="ll-ask">Ask</button>
        <div id="ll-response"></div>
    `;

    document.body.appendChild(panel);
}

function getVideoId() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get("v");
}

function convertToSeconds(timestamp) {
    const parts = timestamp.split(":").map(Number);
    if (parts.length === 3) {
        return parts[0] * 3600 + parts[1] * 60 + parts[2];
    }
    if (parts.length === 2) {
        return parts[0] * 60 + parts[1];
    }
    return 0;
}


function jumpToTimestamp(seconds) {
    const video = document.querySelector("video");

    if (video) {
        video.currentTime = seconds;
        video.play();
    }
}

async function askQuestion() {
    const query = document.getElementById("ll-query").value;
    const videoId = getVideoId();
    const responseDiv = document.getElementById("ll-response");

    responseDiv.innerHTML = "Thinking...";

    const res = await fetch("http://127.0.0.1:8000/query/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            video_id: videoId,
            query: query,
            top_k: 10
        })
    });

    const data = await res.json();

    // Build HTML
    let html = `<p><strong>Answer:</strong><br>${data.answer}</p>`;

    if (data.sources && data.sources.length > 0) {
        html += `<hr><strong>Referenced Timestamps:</strong><ul>`;

        data.sources.forEach(source => {
            html += `
                <li>
                    <button class="ll-timestamp" data-time="${convertToSeconds(source.timestamp)}">
                        ${source.timestamp}
                    </button>
                </li>
            `;
        });

        html += `</ul>`;
    }

    responseDiv.innerHTML = html;
}

createPanel();

document.addEventListener("click", function (e) {
    if (e.target && e.target.id === "ll-ask") {
        askQuestion();
    }
});

document.addEventListener("click", function (e) {
    if (e.target && e.target.classList.contains("ll-timestamp")) {
        const seconds = parseInt(e.target.getAttribute("data-time"));
        jumpToTimestamp(seconds);
    }
});