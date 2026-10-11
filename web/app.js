// Sarvam AI Podcast Studio — Interactive Logic

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const tabTopicBtn = document.getElementById("tabTopicBtn");
  const tabDocBtn = document.getElementById("tabDocBtn");
  const topicMode = document.getElementById("topicMode");
  const docMode = document.getElementById("docMode");
  const topicInput = document.getElementById("topicInput");
  const docTopicHint = document.getElementById("docTopicHint");
  const languageSelect = document.getElementById("languageSelect");
  const languageCodeInput = document.getElementById("languageCodeInput");

  const podcastForm = document.getElementById("podcastForm");
  const btnGenerate = document.getElementById("btnGenerate");
  const progressCard = document.getElementById("progressCard");
  const progressBarFill = document.getElementById("progressBarFill");
  const progressTitle = document.getElementById("progressTitle");
  const progressSubtitle = document.getElementById("progressSubtitle");
  const step1 = document.getElementById("step1");
  const step2 = document.getElementById("step2");
  const step3 = document.getElementById("step3");

  const audioElement = document.getElementById("audioElement");
  const btnPlayPause = document.getElementById("btnPlayPause");
  const playIcon = document.getElementById("playIcon");
  const pauseIcon = document.getElementById("pauseIcon");
  const seekSlider = document.getElementById("seekSlider");
  const currentTimeLabel = document.getElementById("currentTimeLabel");
  const totalDurationLabel = document.getElementById("totalDurationLabel");
  const btnRewind10 = document.getElementById("btnRewind10");
  const btnForward10 = document.getElementById("btnForward10");
  const btnDownloadAudio = document.getElementById("btnDownloadAudio");
  const btnDownloadTranscript = document.getElementById("btnDownloadTranscript");

  const epTitle = document.getElementById("epTitle");
  const epHosts = document.getElementById("epHosts");
  const epLanguageTag = document.getElementById("epLanguageTag");
  const epDurationTag = document.getElementById("epDurationTag");
  const epBgmTag = document.getElementById("epBgmTag");
  const transcriptTurnsList = document.getElementById("transcriptTurnsList");
  const playerStatusPill = document.getElementById("playerStatusPill");

  const btnLibraryToggle = document.getElementById("btnLibraryToggle");
  const libraryDrawer = document.getElementById("libraryDrawer");
  const drawerBackdrop = document.getElementById("drawerBackdrop");
  const btnCloseLibrary = document.getElementById("btnCloseLibrary");
  const libraryEpisodesList = document.getElementById("libraryEpisodesList");
  const episodesCount = document.getElementById("episodesCount");

  const fileDropzone = document.getElementById("fileDropzone");
  const docFileInput = document.getElementById("docFileInput");
  const btnBrowseFile = document.getElementById("btnBrowseFile");
  const dropzoneText = document.getElementById("dropzoneText");

  let currentEpisodeData = null;
  let activeTab = "topic";

  // 1. Tab Switching
  tabTopicBtn.addEventListener("click", () => {
    activeTab = "topic";
    tabTopicBtn.classList.add("active");
    tabDocBtn.classList.remove("active");
    topicMode.classList.add("active");
    docMode.classList.remove("active");
    topicInput.required = true;
  });

  tabDocBtn.addEventListener("click", () => {
    activeTab = "doc";
    tabDocBtn.classList.add("active");
    tabTopicBtn.classList.remove("active");
    docMode.classList.add("active");
    topicMode.classList.remove("active");
    topicInput.required = false;
  });

  // 2. Inspiration Chips
  document.querySelectorAll(".chip-btn").forEach((chip) => {
    chip.addEventListener("click", () => {
      topicInput.value = chip.getAttribute("data-topic");
      topicInput.focus();
    });
  });

  // 3. Language Code Mapping
  languageSelect.addEventListener("change", (e) => {
    const selectedOption = e.target.options[e.target.selectedIndex];
    const code = selectedOption.getAttribute("data-code") || "en-IN";
    languageCodeInput.value = code;

    // Suggest matching voices
    if (selectedOption.value === "Hindi") {
      document.getElementById("host1Voice").value = "aayan";
      document.getElementById("host2Voice").value = "kavya";
      document.getElementById("host1Name").value = "Aayan";
      document.getElementById("host2Name").value = "Kavya";
    } else {
      document.getElementById("host1Voice").value = "rohan";
      document.getElementById("host2Voice").value = "priya";
      document.getElementById("host1Name").value = "Rohan";
      document.getElementById("host2Name").value = "Priya";
    }
  });

  // 4. File Dropzone
  btnBrowseFile.addEventListener("click", () => docFileInput.click());
  fileDropzone.addEventListener("click", (e) => {
    if (e.target !== btnBrowseFile) docFileInput.click();
  });

  docFileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      dropzoneText.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
      if (!docTopicHint.value) {
        docTopicHint.value = file.name.replace(/\.[^/.]+$/, "").replace(/_/g, " ");
      }
    }
  });

  // 5. Audio Player Controls
  btnPlayPause.addEventListener("click", () => {
    if (audioElement.paused) {
      audioElement.play();
    } else {
      audioElement.pause();
    }
  });

  audioElement.addEventListener("play", () => {
    playIcon.classList.add("hidden");
    pauseIcon.classList.remove("hidden");
  });

  audioElement.addEventListener("pause", () => {
    playIcon.classList.remove("hidden");
    pauseIcon.classList.add("hidden");
  });

  audioElement.addEventListener("timeupdate", () => {
    if (audioElement.duration) {
      const progress = (audioElement.currentTime / audioElement.duration) * 100;
      seekSlider.value = progress;
      currentTimeLabel.textContent = formatTime(audioElement.currentTime);
      totalDurationLabel.textContent = formatTime(audioElement.duration);
    }
  });

  seekSlider.addEventListener("input", () => {
    if (audioElement.duration) {
      audioElement.currentTime = (seekSlider.value / 100) * audioElement.duration;
    }
  });

  btnRewind10.addEventListener("click", () => {
    audioElement.currentTime = Math.max(0, audioElement.currentTime - 10);
  });

  btnForward10.addEventListener("click", () => {
    if (audioElement.duration) {
      audioElement.currentTime = Math.min(audioElement.duration, audioElement.currentTime + 10);
    }
  });

  // Speed chips
  ["btnSpeed1", "btnSpeed125", "btnSpeed15"].forEach((id) => {
    const btn = document.getElementById(id);
    btn.addEventListener("click", () => {
      document.querySelectorAll(".speed-selector .btn-chip").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const speed = id === "btnSpeed1" ? 1.0 : id === "btnSpeed125" ? 1.25 : 1.5;
      audioElement.playbackRate = speed;
    });
  });

  function formatTime(seconds) {
    if (isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  }

  // 6. Generate Form Submit
  podcastForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(podcastForm);

    // If doc mode, ensure topic is provided from hint or file
    if (activeTab === "doc") {
      const hint = docTopicHint.value.trim();
      const file = docFileInput.files[0];
      if (!file) {
        alert("Please select a document file (.pdf, .txt, .md)");
        return;
      }
      formData.set("topic", hint || file.name.replace(/\.[^/.]+$/, ""));
    }

    // UI Loading state
    btnGenerate.disabled = true;
    btnGenerate.querySelector(".btn-text").classList.add("hidden");
    btnGenerate.querySelector(".btn-spinner").classList.remove("hidden");

    progressCard.classList.remove("hidden");
    progressBarFill.style.width = "15%";
    progressTitle.textContent = "Researching & Structuring Episode...";
    progressSubtitle.textContent = "Writing natural two-host dialogue with Sarvam-105B";
    step1.className = "progress-step active";
    step2.className = "progress-step";
    step3.className = "progress-step";
    playerStatusPill.textContent = "Generating...";

    // Simulated step animation for responsiveness while processing
    const timer1 = setTimeout(() => {
      progressBarFill.style.width = "45%";
      step1.className = "progress-step done";
      step2.className = "progress-step active";
      progressTitle.textContent = "Synthesizing Host Voices with Bulbul v3...";
      progressSubtitle.textContent = "Generating natural cadence, emotion, and pauses";
    }, 4000);

    const timer2 = setTimeout(() => {
      progressBarFill.style.width = "80%";
      step2.className = "progress-step done";
      step3.className = "progress-step active";
      progressTitle.textContent = "Mastering Audio & Blending Background Music...";
      progressSubtitle.textContent = "Applying dynamic audio ducking and intro jingle";
    }, 12000);

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        body: formData,
      });

      clearTimeout(timer1);
      clearTimeout(timer2);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Generation failed");
      }

      const data = await response.json();
      progressBarFill.style.width = "100%";
      step3.className = "progress-step done";
      progressTitle.textContent = "Episode Mastered Successfully!";
      progressSubtitle.textContent = "Ready for playback and export";

      setTimeout(() => {
        progressCard.classList.add("hidden");
      }, 2000);

      loadEpisodeIntoStudio(data.episode);
      loadEpisodesLibrary();
    } catch (err) {
      clearTimeout(timer1);
      clearTimeout(timer2);
      alert(`Error generating episode: ${err.message}`);
      progressCard.classList.add("hidden");
    } finally {
      btnGenerate.disabled = false;
      btnGenerate.querySelector(".btn-text").classList.remove("hidden");
      btnGenerate.querySelector(".btn-spinner").classList.add("hidden");
      playerStatusPill.textContent = "Ready";
    }
  });

  // 7. Load Episode into Player & Transcript
  function loadEpisodeIntoStudio(ep) {
    currentEpisodeData = ep;
    epTitle.textContent = ep.topic;
    epLanguageTag.textContent = ep.language || "English";
    epDurationTag.textContent = ep.duration_formatted;
    epBgmTag.textContent = ep.bgm_style ? ep.bgm_style.replace("_", " ").toUpperCase() : "Clean Audio";

    const hosts = ep.hosts || { Rohan: "rohan", Priya: "priya" };
    const hostNames = Object.keys(hosts);
    epHosts.innerHTML = `Featuring <strong>${hostNames[0] || "Host 1"}</strong> & <strong>${hostNames[1] || "Host 2"}</strong>`;

    const audioUrl = `/api/audio/${ep.audio_filename}`;
    audioElement.src = audioUrl;
    btnDownloadAudio.href = audioUrl;
    btnDownloadAudio.setAttribute("download", ep.audio_filename);

    // Render Transcript
    transcriptTurnsList.innerHTML = "";
    if (ep.script && Array.isArray(ep.script)) {
      ep.script.forEach((turn, idx) => {
        const card = document.createElement("div");
        card.className = "turn-card";

        const isHost1 = idx % 2 === 0;
        const avatarClass = isHost1 ? "host-1-avatar" : "host-2-avatar";
        const initial = turn.speaker.charAt(0).toUpperCase();

        card.innerHTML = `
          <div class="turn-avatar ${avatarClass}">${initial}</div>
          <div class="turn-content">
            <span class="turn-speaker">${turn.speaker}</span>
            <p class="turn-text">${turn.text}</p>
          </div>
        `;
        transcriptTurnsList.appendChild(card);
      });
    }
  }

  // 8. Download Transcript Markdown
  btnDownloadTranscript.addEventListener("click", () => {
    if (!currentEpisodeData) return;
    let md = `# Podcast Episode: ${currentEpisodeData.topic}\n\n`;
    md += `- **Duration:** ${currentEpisodeData.duration_formatted}\n`;
    md += `- **Language:** ${currentEpisodeData.language}\n\n`;
    md += `## Transcript\n\n`;

    if (currentEpisodeData.script) {
      currentEpisodeData.script.forEach((turn) => {
        md += `**${turn.speaker}**: ${turn.text}\n\n`;
      });
    }

    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${currentEpisodeData.topic.replace(/\s+/g, "_")}_transcript.md`;
    a.click();
    URL.revokeObjectURL(url);
  });

  // 9. Episode Library Drawer
  btnLibraryToggle.addEventListener("click", () => {
    libraryDrawer.classList.add("open");
    drawerBackdrop.classList.add("open");
  });

  const closeDrawer = () => {
    libraryDrawer.classList.remove("open");
    drawerBackdrop.classList.remove("open");
  };

  btnCloseLibrary.addEventListener("click", closeDrawer);
  drawerBackdrop.addEventListener("click", closeDrawer);

  async function loadEpisodesLibrary() {
    try {
      const res = await fetch("/api/episodes");
      if (!res.ok) return;
      const data = await res.json();
      const episodes = data.episodes || [];
      episodesCount.textContent = episodes.length;

      if (episodes.length === 0) {
        libraryEpisodesList.innerHTML = `<p class="empty-state">No episodes generated yet. Produce your first one!</p>`;
        return;
      }

      libraryEpisodesList.innerHTML = "";
      episodes.forEach((ep) => {
        const item = document.createElement("div");
        item.className = "episode-card-library";
        item.innerHTML = `
          <h4 class="lib-ep-title">${ep.topic}</h4>
          <div class="lib-ep-meta">
            <span>⏱️ ${ep.duration_formatted}</span>
            <span>🌐 ${ep.language}</span>
            <span>💬 ${ep.dialogue_count} turns</span>
          </div>
        `;
        item.addEventListener("click", async () => {
          closeDrawer();
          const detailRes = await fetch(`/api/episode/${ep.id}`);
          if (detailRes.ok) {
            const detailData = await detailRes.json();
            detailData.audio_filename = ep.audio_filename;
            loadEpisodeIntoStudio(detailData);
          }
        });
        libraryEpisodesList.appendChild(item);
      });

      // Load initial episode into player if not loaded yet
      if (!currentEpisodeData && episodes.length > 0) {
        const initialRes = await fetch(`/api/episode/${episodes[0].id}`);
        if (initialRes.ok) {
          const initialData = await initialRes.json();
          initialData.audio_filename = episodes[0].audio_filename;
          loadEpisodeIntoStudio(initialData);
        }
      }
    } catch (e) {
      console.error("Failed to load library", e);
    }
  }

  // Initial load
  loadEpisodesLibrary();
});
