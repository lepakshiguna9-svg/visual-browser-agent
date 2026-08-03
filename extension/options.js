const backendUrl = document.querySelector("#backendUrl");
const enabled = document.querySelector("#enabled");
const status = document.querySelector("#status");

chrome.storage.local.get({ backendUrl: "http://localhost:8787", enabled: true }).then((settings) => {
  backendUrl.value = settings.backendUrl;
  enabled.checked = settings.enabled;
});

document.querySelector("#save").addEventListener("click", async () => {
  try {
    const parsed = new URL(backendUrl.value);
    if (!/^https?:$/.test(parsed.protocol)) throw new Error("Backend URL must use HTTP or HTTPS");
    await chrome.storage.local.set({ backendUrl: backendUrl.value.replace(/\/$/, ""), enabled: enabled.checked });
    status.textContent = "Settings saved.";
  } catch (error) {
    status.textContent = error.message;
  }
});
