function createPanel() {
    const panel = document.createElement("div");
    panel.id = "lecturelens-panel";

    panel.innerHTML = `
    <div id="ll-header">
        <h2>LectureLens AI</h2>
        <button id="ll-toggle">−</button>
    </div>

    <!-- Tabs -->
    <div id="ll-tabs">
        <button class="ll-tab active" data-tab="qa">Q/A</button>
        <button class="ll-tab" data-tab="notes">Notes</button>
        <button class="ll-tab" data-tab="flashcards">Flashcards</button>
    </div>

    <!-- Q/A Tab -->
    <div class="ll-tab-content active" id="qa-tab">
        <input type="text" id="ll-query" placeholder="Ask about this video..." />
        <button id="ll-ask">Ask</button>

        <button id="ll-gen-notes">Generate Notes</button>
        <button id="ll-gen-flashcards">Generate Flashcards</button>

        <div id="ll-response"></div>
    </div>

    <!-- Notes Tab -->
    <div class="ll-tab-content" id="notes-tab">
        <h3>Saved Notes</h3>
        <div id="ll-notes-list"></div>
    </div>

    <!-- Flashcards Tab -->
    <div class="ll-tab-content" id="flashcards-tab">
        <h3>Saved Flashcards</h3>
        <div id="ll-flashcards-list"></div>
    </div>
    `;

    document.body.appendChild(panel);
}


async function generateNotes() {
    const videoId = getVideoId();
    const responseDiv = document.getElementById("ll-response");

    responseDiv.innerHTML = "Generating notes...";

    const res = await fetch(`http://127.0.0.1:8000/notes?video_id=${videoId}`, {
        method: "POST"
    });

    const data = await res.json();

    responseDiv.innerHTML = `
        <div>${data.notes}</div>
        <button id="ll-save-notes">Save Notes</button>
    `;
}


async function generateFlashcards() {
    const videoId = getVideoId();
    const responseDiv = document.getElementById("ll-response");

    responseDiv.innerHTML = "Generating flashcards...";

    const res = await fetch(`http://127.0.0.1:8000/flashcards?video_id=${videoId}`, {
        method: "POST"
    });

    const data = await res.json();

    responseDiv.innerHTML = `
        <div>${data.flashcards}</div>
        <button id="ll-save-flashcards">Save Flashcards</button>
    `;
}


async function saveContent(type, content) {
    const videoId = getVideoId();

    await fetch("http://127.0.0.1:8000/save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            video_id: videoId,
            type: type,
            content: content
        })
    });

    alert("Saved!");
}

async function loadSaved(type) {
    const videoId = getVideoId();

    const res = await fetch(`http://127.0.0.1:8000/saved?video_id=${videoId}&type=${type}`);
    const data = await res.json();

    const container = type === "notes"
        ? document.getElementById("ll-notes-list")
        : document.getElementById("ll-flashcards-list");

    container.innerHTML = data.map(item => `
        <div class="ll-card">${item.content}</div>
    `).join("");
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

    if (!video) return;

    const start = video.currentTime;
    const diff = seconds - start;
    const duration = 400;
    const startTime = performance.now();

    function animate(time) {

        const progress = Math.min((time - startTime) / duration, 1);

        video.currentTime = start + diff * progress;

        if (progress < 1) requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);

    video.play();
}

function createFloatingButton() {

    const btn = document.createElement("div");

    btn.id = "ll-floating-btn";

    btn.innerText = "AI";

    document.body.appendChild(btn);

    btn.onclick = () => {

        const panel = document.getElementById("lecturelens-panel");

        panel.style.display =
            panel.style.display === "none" ? "flex" : "none";
    };
}

async function askQuestion() {
    const query = document.getElementById("ll-query").value;
    const videoId = getVideoId();
    const responseDiv = document.getElementById("ll-response");

    responseDiv.innerHTML = `
        <div class="ll-loader"></div>
        <div class="ll-loading-text">LectureLens AI is thinking...</div>
        `;

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
                        ⏱ ${source.timestamp}
                    </button>
                    <div class="ll-snippet">
                        ${source.text}
                    </div>
                </li>
            `;
        });

        html += `</ul>`;
    }

    responseDiv.innerHTML = html;
}

createFloatingButton();
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

document.addEventListener("click", function(e) {

    if (e.target && e.target.id === "ll-toggle") {

        const panel = document.getElementById("lecturelens-panel");

        if (panel.style.width === "60px") {
            panel.style.width = "360px";
        } else {
            panel.style.width = "60px";
        }
    }

});


document.addEventListener("click", function (e) {
    if (e.target.classList.contains("ll-tab")) {
        document.querySelectorAll(".ll-tab").forEach(btn => btn.classList.remove("active"));
        document.querySelectorAll(".ll-tab-content").forEach(tab => tab.classList.remove("active"));

        e.target.classList.add("active");

        const tab = e.target.getAttribute("data-tab");
        document.getElementById(`${tab}-tab`).classList.add("active");
    }
});


document.addEventListener("click", function (e) {

    if (e.target.id === "ll-gen-notes") {
        generateNotes();
    }

    if (e.target.id === "ll-gen-flashcards") {
        generateFlashcards();
    }

    if (e.target.id === "ll-save-notes") {
        const content = document.getElementById("ll-response").innerText;
        saveContent("notes", content);
    }

    if (e.target.id === "ll-save-flashcards") {
        const content = document.getElementById("ll-response").innerText;
        saveContent("flashcard", content);
    }

    if (e.target.dataset.tab === "notes") {
        loadSaved("notes");
    }

    if (e.target.dataset.tab === "flashcards") {
        loadSaved("flashcard");
    }
});