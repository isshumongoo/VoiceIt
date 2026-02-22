const form = document.getElementById("generator-form");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const scriptOut = document.getElementById("script-output");
const scriptLink = document.getElementById("script-link");
const audioLink = document.getElementById("audio-link");
const submitBtn = document.getElementById("submit-btn");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  submitBtn.disabled = true;
  resultEl.classList.add("hidden");
  statusEl.textContent = "Generating... this can take a minute.";

  const payload = {
    topic: document.getElementById("topic").value,
    style: document.getElementById("style").value,
    duration_minutes: Number(document.getElementById("duration").value || 3),
    model: document.getElementById("model").value,
    skip_audio: document.getElementById("skip-audio").checked,
  };

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Failed to generate podcast.");
    }

    scriptOut.textContent = data.script;
    scriptLink.href = `/download/script?path=${encodeURIComponent(data.script_path)}`;

    if (data.audio_path) {
      audioLink.href = `/download/audio?path=${encodeURIComponent(data.audio_path)}`;
      audioLink.style.display = "inline";
    } else {
      audioLink.style.display = "none";
    }

    resultEl.classList.remove("hidden");
    statusEl.textContent = "Podcast created successfully.";
  } catch (error) {
    statusEl.textContent = `Error: ${error.message}`;
  } finally {
    submitBtn.disabled = false;
  }
});
