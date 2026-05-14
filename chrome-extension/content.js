/* ═══════════════════════════════════════════
   LectureLens AI — content.js v2
   UI redesign — core API logic unchanged from original
═══════════════════════════════════════════ */

const API = "http://127.0.0.1:8000";

/* ─── Helpers (identical to original) ─── */
function getVideoId() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get("v");
}

function convertToSeconds(timestamp) {
  const parts = timestamp.split(":").map(Number);
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  return 0;
}

function jumpToTimestamp(seconds) {
  const video = document.querySelector("video");
  if (!video) return;
  video.currentTime = seconds;
  video.play();
}

/* ─── Toast ─── */
function showToast(msg, type) {
  let t = document.getElementById("ll-toast");
  if (!t) {
    t = document.createElement("div");
    t.id = "ll-toast";
    t.className = "ll-toast";
    document.body.appendChild(t);
  }
  const color = type === "error" ? "#f87171" : "#34d399";
  t.innerHTML = '<div class="ll-toast-dot" style="background:' + color + '"></div>' + msg;
  t.classList.add("show");
  clearTimeout(t._timer);
  t._timer = setTimeout(function() { t.classList.remove("show"); }, 2800);
}

/* ─── Panel visibility ─── */
var panelVisible = true;

/* ══════════════════════════════════
   FLOATING BUTTON
══════════════════════════════════ */
function createFloatingButton() {
  var btn = document.createElement("div");
  btn.id = "ll-floating-btn";
  btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>';
  document.body.appendChild(btn);
  btn.onclick = function() {
    panelVisible = !panelVisible;
    var panel = document.getElementById("lecturelens-panel");
    panel.style.display = panelVisible ? "flex" : "none";
  };
}

/* ══════════════════════════════════
   CREATE PANEL
══════════════════════════════════ */
function createPanel() {
  var panel = document.createElement("div");
  panel.id = "lecturelens-panel";

  var videoId = getVideoId();
  var thumbUrl = videoId ? "https://img.youtube.com/vi/" + videoId + "/mqdefault.jpg" : "";

  panel.innerHTML =
    '<div id="ll-resize-handle"></div>' +

    '<div id="ll-header">' +
      '<div class="ll-header-top">' +
        '<div class="ll-brand">' +
          '<div class="ll-brand-icon">' +
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4f9eff" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>' +
          '</div>' +
          '<span class="ll-brand-name">LectureLens</span>' +
          '<span class="ll-brand-badge">AI</span>' +
        '</div>' +
        '<div class="ll-header-actions">' +
          '<button class="ll-icon-btn" id="ll-btn-wide" title="Wide mode"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg></button>' +
          '<button class="ll-icon-btn" id="ll-btn-fullscreen" title="Fullscreen"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/></svg></button>' +
          '<button class="ll-icon-btn" id="ll-btn-close" title="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>' +
        '</div>' +
      '</div>' +
      '<div class="ll-video-ctx">' +
        '<div class="ll-video-thumb">' + (thumbUrl ? '<img src="' + thumbUrl + '" alt="">' : "") + '</div>' +
        '<div class="ll-video-info">' +
          '<div class="ll-video-title" id="ll-video-title">Loading...</div>' +
          '<div class="ll-video-sub">YouTube · Active</div>' +
        '</div>' +
        '<div class="ll-status-dot"></div>' +
      '</div>' +
    '</div>' +

    '<div id="ll-tabs">' +
      '<button class="ll-tab active" data-tab="qa"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>Ask AI</button>' +
      '<button class="ll-tab" data-tab="notes"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>Notes</button>' +
      '<button class="ll-tab" data-tab="flashcards"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>Cards</button>' +
    '</div>' +

    '<div class="ll-tab-content active" id="qa-tab">' +
      '<div class="ll-search-wrap">' +
        '<svg class="ll-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>' +
        '<input type="text" id="ll-query" placeholder="Ask about this video..." autocomplete="off" />' +
      '</div>' +
      '<div class="ll-action-row">' +
        '<button class="ll-btn-primary" id="ll-ask"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>Ask</button>' +
        '<button class="ll-btn-secondary" id="ll-gen-notes"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>Notes</button>' +
        '<button class="ll-btn-secondary" id="ll-gen-flashcards"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>Cards</button>' +
      '</div>' +
      '<div class="ll-quick-btns">' +
        '<span class="ll-quick-chip" data-q="Summarize this video">Summarize</span>' +
        '<span class="ll-quick-chip" data-q="What are the key concepts?">Key concepts</span>' +
        '<span class="ll-quick-chip" data-q="What are the main takeaways?">Takeaways</span>' +
      '</div>' +
      '<div id="ll-response">' +
        '<div class="ll-empty">' +
          '<div class="ll-empty-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>' +
          '<p>Ask a question to get started</p>' +
          '<span>or tap a quick prompt above</span>' +
        '</div>' +
      '</div>' +
    '</div>' +

    '<div class="ll-tab-content" id="notes-tab">' +
      '<div class="ll-section-header">' +
        '<div class="ll-section-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>Saved Notes</div>' +
        '<span class="ll-count-badge" id="ll-notes-count">0</span>' +
      '</div>' +
      '<div class="ll-notes-list" id="ll-notes-list">' +
        '<div class="ll-empty"><div class="ll-empty-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/></svg></div><p>No notes yet</p></div>' +
      '</div>' +
    '</div>' +

    '<div class="ll-tab-content" id="flashcards-tab">' +
      '<div class="ll-section-header">' +
        '<div class="ll-section-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>Flashcards</div>' +
        '<span class="ll-count-badge" id="ll-cards-count">0</span>' +
      '</div>' +
      '<div class="ll-fc-progress">' +
        '<div class="ll-fc-progress-text" id="ll-fc-prog-text">0 / 0 revealed</div>' +
        '<div class="ll-fc-progress-bar"><div class="ll-fc-progress-fill" id="ll-fc-prog-fill" style="width:0%"></div></div>' +
      '</div>' +
      '<div class="ll-flashcards-list" id="ll-flashcards-list">' +
        '<div class="ll-empty"><div class="ll-empty-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="7" width="20" height="14" rx="2"/></svg></div><p>No flashcards yet</p></div>' +
      '</div>' +
    '</div>' +

    '<div id="ll-toast" class="ll-toast"></div>';

  document.body.appendChild(panel);
  initEvents();
  loadVideoTitle();
}

/* ══════════════════════════════════
   INIT ALL EVENTS
══════════════════════════════════ */
function initEvents() {
  /* tabs */
  document.querySelectorAll(".ll-tab").forEach(function(btn) {
    btn.addEventListener("click", function() {
      document.querySelectorAll(".ll-tab").forEach(function(b) { b.classList.remove("active"); });
      document.querySelectorAll(".ll-tab-content").forEach(function(t) { t.classList.remove("active"); });
      btn.classList.add("active");
      var tab = btn.getAttribute("data-tab");
      document.getElementById(tab + "-tab").classList.add("active");
      if (tab === "notes")      loadSaved("notes");
      if (tab === "flashcards") loadSaved("flashcard");
    });
  });

  /* ask */
  document.getElementById("ll-ask").addEventListener("click", askQuestion);

  /* enter key */
  document.getElementById("ll-query").addEventListener("keydown", function(e) {
    if (e.key === "Enter") { e.preventDefault(); askQuestion(); }
  });

  /* quick chips */
  document.querySelectorAll(".ll-quick-chip").forEach(function(chip) {
    chip.addEventListener("click", function() {
      document.getElementById("ll-query").value = chip.getAttribute("data-q");
      askQuestion();
    });
  });

  /* notes + flashcards generate buttons */
  document.getElementById("ll-gen-notes").addEventListener("click", generateNotes);
  document.getElementById("ll-gen-flashcards").addEventListener("click", generateFlashcards);

  /* header controls */
  document.getElementById("ll-btn-wide").addEventListener("click", function() {
    var p = document.getElementById("lecturelens-panel");
    p.classList.toggle("wide");
    p.classList.remove("fullscreen");
  });
  document.getElementById("ll-btn-fullscreen").addEventListener("click", function() {
    var p = document.getElementById("lecturelens-panel");
    p.classList.toggle("fullscreen");
    p.classList.remove("wide");
  });
  document.getElementById("ll-btn-close").addEventListener("click", function() {
    document.getElementById("lecturelens-panel").style.display = "none";
    panelVisible = false;
  });

  /* resize handle */
  var handle = document.getElementById("ll-resize-handle");
  var dragging = false, startX = 0, startW = 0;
  handle.addEventListener("mousedown", function(e) {
    dragging = true;
    startX = e.clientX;
    startW = document.getElementById("lecturelens-panel").offsetWidth;
    document.body.style.userSelect = "none";
  });
  document.addEventListener("mousemove", function(e) {
    if (!dragging) return;
    var newW = Math.min(Math.max(startW + (startX - e.clientX), 320), window.innerWidth * 0.9);
    document.getElementById("lecturelens-panel").style.width = newW + "px";
  });
  document.addEventListener("mouseup", function() {
    dragging = false;
    document.body.style.userSelect = "";
  });
}

/* ══════════════════════════════════
   VIDEO TITLE
══════════════════════════════════ */
function loadVideoTitle() {
  setTimeout(function() {
    var el = document.querySelector("h1.ytd-video-primary-info-renderer yt-formatted-string")
          || document.querySelector("#above-the-fold #title yt-formatted-string")
          || document.querySelector("h1.title");
    var el2 = document.getElementById("ll-video-title");
    if (el2 && el) el2.textContent = el.textContent.trim() || "YouTube Video";
  }, 1500);
}

/* ══════════════════════════════════
   ASK QUESTION  ← exact same as original
══════════════════════════════════ */
async function askQuestion() {
  var query = document.getElementById("ll-query").value;
  var videoId = getVideoId();
  var responseDiv = document.getElementById("ll-response");

  responseDiv.innerHTML =
    '<div class="ll-loading-wrap">' +
      '<div class="ll-loader-ring"></div>' +
      '<div class="ll-loading-text">LectureLens AI is thinking...</div>' +
    '</div>';

  try {
    var res = await fetch("http://127.0.0.1:8000/query/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        video_id: videoId,
        query: query,
        top_k: 10
      })
    });

    var data = await res.json();

    /* Answer section */
    var html = 
      '<div class="ll-answer-card">' +
        '<div class="ll-answer-label">Answer</div>' +
        '<p>' + data.answer + '</p>' +
      '</div>';

    /* ✅ Confidence Badge */
    if (data.confidence) {
      var confClass = "ll-" + data.confidence.label.toLowerCase();

      html += 
        '<div class="ll-confidence ' + confClass + '">' +
          data.confidence.badge + ' ' + data.confidence.label + ' confidence' +
        '</div>';
    }

    /* Timestamps section */
    if (data.sources && data.sources.length > 0) {
      html += '<div class="ll-timestamps-header">Referenced Timestamps</div>';
      data.sources.forEach(function(source) {
        var secs = convertToSeconds(source.timestamp);
        var snippet = (source.text || "").slice(0, 120);
        html +=
          '<div class="ll-timestamp-item">' +
            '<button class="ll-timestamp-btn ll-timestamp" data-time="' + secs + '">' +
              '<span class="ll-timestamp-badge">' + source.timestamp + '</span>' +
              '<span class="ll-timestamp-label">' + (snippet || "Jump to this moment") + '</span>' +
              '<span class="ll-timestamp-play"><svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg></span>' +
            '</button>' +
            (snippet ? '<div class="ll-snippet">' + snippet + '</div>' : '') +
          '</div>';
      });
    }

    responseDiv.innerHTML = html;

    /* Attach timestamp clicks AFTER innerHTML is set */
    responseDiv.querySelectorAll(".ll-timestamp").forEach(function(btn) {
      btn.addEventListener("click", function() {
        jumpToTimestamp(parseInt(btn.getAttribute("data-time")));
      });
    });

  } catch (error) {
    responseDiv.innerHTML =
      '<div class="ll-answer-card" style="border-left-color:var(--danger)">' +
        '<div class="ll-answer-label" style="color:var(--danger)">Error</div>' +
        'Something went wrong.' +
      '</div>';
    console.error(error);
  }
}

/* ══════════════════════════════════
   GENERATE NOTES  ← exact same as original
══════════════════════════════════ */
async function generateNotes() {
  var videoId = getVideoId();
  var query = document.getElementById("ll-query").value;
  var responseDiv = document.getElementById("ll-response");

  responseDiv.innerHTML =
    '<div class="ll-loading-wrap"><div class="ll-loader-ring"></div><div class="ll-loading-text">Generating notes...</div></div>';

  var url = query
    ? "http://127.0.0.1:8000/notes?video_id=" + videoId + "&query=" + encodeURIComponent(query)
    : "http://127.0.0.1:8000/notes?video_id=" + videoId;

  var res = await fetch(url, { method: "POST" });
  var data = await res.json();

  if (!data.notes) {
    responseDiv.innerHTML = '<div class="ll-answer-card">Error generating notes</div>';
    return;
  }

  responseDiv.innerHTML =
    '<div class="ll-answer-card">' +
      '<div class="ll-answer-label">Generated Notes</div>' +
      '<div style="white-space:pre-wrap;line-height:1.7;font-size:13px;color:var(--text-secondary)">' + data.notes + '</div>' +
    '</div>' +
    '<button class="ll-btn-primary" id="ll-save-notes">Save Notes</button>';

  document.getElementById("ll-save-notes").addEventListener("click", function() {
    saveContent("notes", data.notes);
  });
}

/* ══════════════════════════════════
   GENERATE FLASHCARDS  ← exact same as original
══════════════════════════════════ */
async function generateFlashcards() {
  var videoId = getVideoId();
  var query = document.getElementById("ll-query").value;
  var responseDiv = document.getElementById("ll-response");

  responseDiv.innerHTML =
    '<div class="ll-loading-wrap">' +
      '<div class="ll-loader-ring"></div>' +
      '<div class="ll-loading-text">Generating flashcards...</div>' +
    '</div>';

  try {
    var url = query
      ? API + "/flashcards?video_id=" + videoId + "&query=" + encodeURIComponent(query)
      : API + "/flashcards?video_id=" + videoId;

    var res = await fetch(url, { method: "POST" });
    var data = await res.json();

    if (!data.flashcards) {
      responseDiv.innerHTML =
        '<div class="ll-answer-card">Error generating flashcards</div>';
      return;
    }

    responseDiv.innerHTML =
      '<div class="ll-answer-card">' +
        '<div class="ll-answer-label">Generated Flashcards</div>' +
        '<div style="white-space:pre-wrap;line-height:1.7;font-size:13px;color:var(--text-secondary)">' +
          data.flashcards +
        '</div>' +
      '</div>' +
      '<button class="ll-btn-primary" id="ll-save-flashcards">Save Flashcards</button>';

    document.getElementById("ll-save-flashcards").addEventListener("click", function () {
      saveContent("flashcard", data.flashcards);
    });

  } catch (error) {
    responseDiv.innerHTML =
      '<div class="ll-answer-card" style="border-left-color:var(--danger)">Failed to generate flashcards</div>';
    console.error(error);
  }
}

/* ══════════════════════════════════
   SAVE CONTENT  ← exact same as original
══════════════════════════════════ */
async function saveContent(type, content) {
  var videoId = getVideoId();
  await fetch("http://127.0.0.1:8000/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_id: videoId, type: type, content: content })
  });
  showToast("Saved!");
}

/* ══════════════════════════════════
   LOAD SAVED  ← exact same as original
══════════════════════════════════ */
async function loadSaved(type) {
  var videoId = getVideoId();
  var isNotes = type === "notes";
  var container = document.getElementById(isNotes ? "ll-notes-list" : "ll-flashcards-list");
  var countEl = document.getElementById(isNotes ? "ll-notes-count" : "ll-cards-count");

  container.innerHTML = '<div class="ll-loading-wrap"><div class="ll-loader-ring"></div></div>';

  try {
    var res = await fetch("http://127.0.0.1:8000/saved?video_id=" + videoId + "&type=" + type);
    var items = await res.json();

    if (countEl) countEl.textContent = items.length;

    if (!items.length) {
      container.innerHTML =
        '<div class="ll-empty">' +
          '<div class="ll-empty-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">' +
            (isNotes ? '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>'
                     : '<rect x="2" y="7" width="20" height="14" rx="2"/>') +
          '</svg></div>' +
          '<p>No ' + (isNotes ? "notes" : "flashcards") + ' yet</p>' +
        '</div>';
      return;
    }

    if (isNotes) {
      container.innerHTML = items.map(function(item, i) { return renderNoteCard(item, i); }).join("");
      container.querySelectorAll(".ll-note-header").forEach(function(h) {
        h.addEventListener("click", function() { h.closest(".ll-note-card").classList.toggle("expanded"); });
      });
      container.querySelectorAll(".ll-note-action-btn.copy").forEach(function(btn) {
        btn.addEventListener("click", function(e) {
          e.stopPropagation();
          navigator.clipboard.writeText(btn.getAttribute("data-content") || "");
          showToast("Copied!");
        });
      });
    } else {
      renderFlashcardsList(items, container);
    }
  } catch(err) {
    container.innerHTML = '<div class="ll-answer-card" style="border-left-color:var(--danger)">Failed to load.</div>';
  }
}

/* ══════════════════════════════════
   RENDER NOTE CARD (accordion)
══════════════════════════════════ */
function renderNoteCard(item, i) {
  var title   = item.title || ("Note " + (i + 1));
  var content = item.content || "";
  var time    = item.created_at ? new Date(item.created_at).toLocaleString() : "";
  return (
    '<div class="ll-note-card">' +
      '<div class="ll-note-header">' +
        '<div class="ll-note-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>' +
        '<div class="ll-note-meta">' +
          '<div class="ll-note-title">' + title + '</div>' +
          (time ? '<div class="ll-note-time">' + time + '</div>' : '') +
        '</div>' +
        '<div class="ll-note-chevron"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg></div>' +
      '</div>' +
      '<div class="ll-note-body">' +
        '<div style="white-space:pre-wrap;line-height:1.7">' + content + '</div>' +
        '<div class="ll-note-actions">' +
          '<button class="ll-note-action-btn copy" data-content="' + escapeAttr(content) + '">' +
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>' +
            'Copy' +
          '</button>' +
        '</div>' +
      '</div>' +
    '</div>'
  );
}

/* ══════════════════════════════════
   RENDER FLASHCARDS (Q/A reveal)
══════════════════════════════════ */
function renderFlashcardsList(items, container) {
  var cards = [];
  items.forEach(function(item) {
    var raw = item.content || "";
    var matches = Array.from(raw.matchAll(/Q:\s*(.*?)\s*A:\s*([\s\S]*?)(?=Q:|$)/gi));
    if (matches.length) {
      matches.forEach(function(m) { cards.push({ q: m[1].trim(), a: m[2].trim() }); });
    } else {
      cards.push({ q: item.title || "Question", a: raw });
    }
  });

  var countEl = document.getElementById("ll-cards-count");
  if (countEl) countEl.textContent = cards.length;
  updateProgress(0, cards.length);

  container.innerHTML = cards.map(function(c, i) {
    return (
      '<div class="ll-flashcard" data-idx="' + i + '">' +
        '<div class="ll-fc-question">' +
          '<div class="ll-fc-q-badge">Q</div>' +
          '<div class="ll-fc-q-text">' + c.q + '</div>' +
          '<button class="ll-fc-reveal-btn">Reveal</button>' +
        '</div>' +
        '<div class="ll-fc-answer">' +
          '<div class="ll-fc-a-label"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Answer</div>' +
          '<div class="ll-fc-a-text">' + c.a + '</div>' +
        '</div>' +
      '</div>'
    );
  }).join("");

  container.querySelectorAll(".ll-fc-reveal-btn").forEach(function(btn) {
    btn.addEventListener("click", function() {
      btn.closest(".ll-flashcard").classList.add("revealed");
      var revealed = container.querySelectorAll(".ll-flashcard.revealed").length;
      updateProgress(revealed, cards.length);
    });
  });
}

function updateProgress(revealed, total) {
  var t = document.getElementById("ll-fc-prog-text");
  var b = document.getElementById("ll-fc-prog-fill");
  if (t) t.textContent = revealed + " / " + total + " revealed";
  if (b) b.style.width = total ? ((revealed / total) * 100) + "%" : "0%";
}

function escapeAttr(s) {
  return (s || "").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

/* ══════════════════════════════════
   INIT
══════════════════════════════════ */
createFloatingButton();
createPanel();