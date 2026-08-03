const DEFAULT_SETTINGS = {
  backendUrl: "http://localhost:8787",
  enabled: true
};

async function getSettings() {
  return chrome.storage.local.get(DEFAULT_SETTINGS);
}

async function postEvent(event) {
  const settings = await getSettings();
  if (!settings.enabled || !event.url || event.url.startsWith("chrome://")) return;

  try {
    const response = await fetch(`${settings.backendUrl}/api/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(event)
    });
    if (!response.ok) console.warn("Backend rejected browser event", response.status);
  } catch (error) {
    console.warn("Backend unavailable; event was not stored", error);
  }
}

function buildEvent(tab, source) {
  return {
    event_type: "page_view",
    url: tab.url || "",
    title: tab.title || "",
    timestamp: new Date().toISOString(),
    source
  };
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete") postEvent(buildEvent(tab, "tabs.onUpdated"));
});

chrome.tabs.onActivated.addListener(async ({ tabId }) => {
  const tab = await chrome.tabs.get(tabId);
  postEvent(buildEvent(tab, "tabs.onActivated"));
});

chrome.runtime.onInstalled.addListener(async () => {
  const current = await chrome.storage.local.get(DEFAULT_SETTINGS);
  await chrome.storage.local.set({ ...DEFAULT_SETTINGS, ...current });
});
