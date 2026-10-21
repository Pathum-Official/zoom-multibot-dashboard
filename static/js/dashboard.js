// Zoom Bot Dashboard JavaScript Controller
let lastLogId = 0;
let isSessionRunning = false;
let presets = {};

// DOM Elements
const globalStatusPill = document.getElementById("global-status-pill");
const globalStatusText = document.getElementById("global-status-text");
const btnQuickStart = document.getElementById("btn-quick-start");
const btnQuickStop = document.getElementById("btn-quick-stop");
const btnStartForm = document.getElementById("btn-start-form");
const btnSaveCfg = document.getElementById("btn-save-cfg");

const metricActiveBots = document.getElementById("metric-active-bots");
const metricTargetBots = document.getElementById("metric-target-bots");
const metricMeetingId = document.getElementById("metric-meeting-id");
const metricUptime = document.getElementById("metric-uptime");
const metricMode = document.getElementById("metric-mode");

const cfgMeetingId = document.getElementById("cfg-meeting-id");
const cfgPassword = document.getElementById("cfg-password");
const cfgCount = document.getElementById("cfg-count");
const valCountBubble = document.getElementById("val-count-bubble");
const cfgDelay = document.getElementById("cfg-delay");
const valDelayBubble = document.getElementById("val-delay-bubble");
const cfgHeadless = document.getElementById("cfg-headless");
const cfgNamesTextarea = document.getElementById("cfg-names-textarea");
const namesCountBadge = document.getElementById("names-count-badge");
const presetSelect = document.getElementById("preset-select");
const btnShuffleNames = document.getElementById("btn-shuffle-names");
const btnClearNames = document.getElementById("btn-clear-names");

const botsTbody = document.getElementById("bots-tbody");
const activeBotsSummary = document.getElementById("active-bots-summary");
const terminalLogs = document.getElementById("terminal-logs");
const autoscrollChk = document.getElementById("autoscroll-chk");
const btnClearTerminal = document.getElementById("btn-clear-terminal");
const togglePwdBtn = document.getElementById("toggle-pwd-btn");

// Init
document.addEventListener("DOMContentLoaded", () => {
    setupEventListeners();
    loadPresets();
    loadConfig();
    startPolling();
});

function setupEventListeners() {
    // Slider bubble binders
    cfgCount.addEventListener("input", (e) => {
        valCountBubble.textContent = e.target.value;
    });

    cfgDelay.addEventListener("input", (e) => {
        valDelayBubble.textContent = e.target.value + "s";
    });

    cfgHeadless.addEventListener("change", (e) => {
        metricMode.textContent = e.target.checked ? "Headless Mode" : "Headed (Auto-Minimized)";
    });

    // Password view toggle
    togglePwdBtn.addEventListener("click", () => {
        const type = cfgPassword.getAttribute("type") === "password" ? "text" : "password";
        cfgPassword.setAttribute("type", type);
    });

    // Preset selection
    presetSelect.addEventListener("change", (e) => {
        const key = e.target.value;
        if (presets[key]) {
            cfgNamesTextarea.value = presets[key].join("\n");
            updateNamesCount();
            showToast(`Loaded ${presets[key].length} names from preset!`, "info");
        }
    });

    // Names textarea live count
    cfgNamesTextarea.addEventListener("input", updateNamesCount);

    // Shuffle names
    btnShuffleNames.addEventListener("click", () => {
        const names = getNamesArray();
        if (names.length === 0) return;
        for (let i = names.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [names[i], names[j]] = [names[j], names[i]];
        }
        cfgNamesTextarea.value = names.join("\n");
        showToast("Names shuffled randomly!", "info");
    });

    // Clear names
    btnClearNames.addEventListener("click", () => {
        cfgNamesTextarea.value = "";
        updateNamesCount();
    });

    // Start Buttons
    btnQuickStart.addEventListener("click", handleStart);
    btnStartForm.addEventListener("click", handleStart);

    // Stop Button
    btnQuickStop.addEventListener("click", handleStop);

    // Save Config
    btnSaveCfg.addEventListener("click", handleSaveConfig);

    // Clear Terminal
    btnClearTerminal.addEventListener("click", () => {
        terminalLogs.innerHTML = "";
        fetch("/api/logs/clear", { method: "POST" });
    });
}

function updateNamesCount() {
    const names = getNamesArray();
    namesCountBadge.textContent = `${names.length} Names`;
}

function getNamesArray() {
    return cfgNamesTextarea.value
        .split("\n")
        .map(n => n.trim())
        .filter(n => n.length > 0);
}

// Load presets from server
async function loadPresets() {
    try {
        const res = await fetch("/api/presets");
        presets = await res.json();
    } catch (e) {
        console.error("Error loading presets:", e);
    }
}

// Load saved config
async function loadConfig() {
    try {
        const res = await fetch("/api/config");
        const cfg = await res.json();
        if (cfg) {
            cfgMeetingId.value = cfg.meeting_id || "";
            cfgPassword.value = cfg.password || "";
            cfgCount.value = cfg.account_count || 5;
            valCountBubble.textContent = cfg.account_count || 5;
            cfgDelay.value = cfg.delay_seconds || 12;
            valDelayBubble.textContent = (cfg.delay_seconds || 12) + "s";
            cfgHeadless.checked = !!cfg.headless;
            metricMode.textContent = cfg.headless ? "Headless Mode" : "Headed (Auto-Minimized)";

            if (cfg.name_list && Array.isArray(cfg.name_list)) {
                cfgNamesTextarea.value = cfg.name_list.join("\n");
            } else if (presets["sinhala"]) {
                cfgNamesTextarea.value = presets["sinhala"].join("\n");
            }
            updateNamesCount();
        }
    } catch (e) {
        console.error("Error loading config:", e);
    }
}

// Save config
async function handleSaveConfig() {
    const payload = {
        meeting_id: cfgMeetingId.value.trim(),
        password: cfgPassword.value.trim(),
        account_count: parseInt(cfgCount.value),
        delay_seconds: parseInt(cfgDelay.value),
        headless: cfgHeadless.checked,
        name_list: getNamesArray()
    };

    try {
        const res = await fetch("/api/config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            showToast("Settings successfully saved to config.json!", "success");
        } else {
            showToast("Failed to save settings.", "error");
        }
    } catch (e) {
        showToast("Error saving settings.", "error");
    }
}

// Start Bots
async function handleStart() {
    const meetingId = cfgMeetingId.value.trim();
    if (!meetingId) {
        showToast("Please enter a valid Zoom Meeting ID!", "error");
        cfgMeetingId.focus();
        return;
    }

    const payload = {
        meeting_id: meetingId,
        password: cfgPassword.value.trim(),
        account_count: parseInt(cfgCount.value),
        delay_seconds: parseInt(cfgDelay.value),
        headless: cfgHeadless.checked,
        name_list: getNamesArray()
    };

    btnStartForm.disabled = true;
    btnQuickStart.disabled = true;

    try {
        const res = await fetch("/api/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            showToast("Bot session launched successfully!", "success");
        } else {
            showToast(data.message || "Failed to start bots.", "error");
            btnStartForm.disabled = false;
            btnQuickStart.disabled = false;
        }
    } catch (e) {
        showToast("Network error starting bots.", "error");
        btnStartForm.disabled = false;
        btnQuickStart.disabled = false;
    }
}

// Stop Bots
async function handleStop() {
    btnQuickStop.disabled = true;
    try {
        const res = await fetch("/api/stop", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "Stopping all bots...", "warning");
    } catch (e) {
        showToast("Error stopping bots.", "error");
    }
}

// Stop Single Bot
async function stopSingleBot(botId) {
    try {
        const res = await fetch(`/api/stop/${botId}`, { method: "POST" });
        const data = await res.json();
        showToast(data.message, "info");
    } catch (e) {
        showToast(`Failed to stop Bot #${botId}`, "error");
    }
}

// Polling Loop (Status + Logs)
function startPolling() {
    setInterval(fetchStatus, 1000);
    setInterval(fetchLogs, 1200);
}

async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        const data = await res.json();
        if (!data) return;

        isSessionRunning = data.is_running;

        // UI state toggle
        btnQuickStart.disabled = isSessionRunning;
        btnStartForm.disabled = isSessionRunning;
        btnQuickStop.disabled = !isSessionRunning && data.active_count === 0;

        // Metrics
        metricActiveBots.textContent = data.active_count;
        metricTargetBots.textContent = `/ ${data.total_target || 0}`;
        metricMeetingId.textContent = data.meeting_id || "---";
        metricUptime.textContent = data.uptime || "00:00:00";

        // Global status pill
        if (isSessionRunning) {
            globalStatusText.textContent = `Running (${data.active_count} Bots Active)`;
            globalStatusPill.className = "status-indicator status-running";
        } else if (data.active_count > 0) {
            globalStatusText.textContent = `Holding (${data.active_count} Bots Connected)`;
            globalStatusPill.className = "status-indicator status-holding";
        } else {
            globalStatusText.textContent = "System Ready";
            globalStatusPill.className = "status-indicator";
        }

        // Render Bots Table
        renderBotsTable(data.bots || []);
    } catch (e) {
        // server might be restarting
    }
}

function renderBotsTable(bots) {
    if (bots.length === 0) {
        botsTbody.innerHTML = `
            <tr class="empty-row">
                <td colspan="6">
                    <div class="empty-state">
                        <span class="empty-icon">🤖</span>
                        <p>No bots currently active. Click "Launch Bots" above to start.</p>
                    </div>
                </td>
            </tr>
        `;
        activeBotsSummary.textContent = "No active instances";
        return;
    }

    activeBotsSummary.textContent = `${bots.length} instances tracked`;

    let html = "";
    bots.forEach(b => {
        const badgeClass = `badge-${b.status}`;
        html += `
            <tr>
                <td><strong>#${b.id}</strong></td>
                <td>
                    <div style="font-weight: 600;">${escapeHtml(b.name)}</div>
                </td>
                <td>
                    <span class="bot-badge ${badgeClass}">${escapeHtml(b.status_text)}</span>
                </td>
                <td>
                    <span style="font-size: 0.8rem; color: var(--text-muted);">${b.headless ? "Headless" : "Visible"}</span>
                </td>
                <td>
                    <span style="font-family: var(--font-mono); font-size: 0.85rem;">${b.duration}</span>
                </td>
                <td class="text-right">
                    ${b.status !== "closed" ? `
                        <button class="btn btn-sm btn-outline" style="color: var(--danger); border-color: rgba(239, 68, 68, 0.3);" onclick="stopSingleBot(${b.id})">
                            Disconnect
                        </button>
                    ` : `
                        <span style="color: var(--text-muted); font-size: 0.78rem;">Closed</span>
                    `}
                </td>
            </tr>
        `;
    });

    botsTbody.innerHTML = html;
}

// Fetch logs
async function fetchLogs() {
    try {
        const res = await fetch(`/api/logs?since=${lastLogId}`);
        const data = await res.json();
        if (data.logs && data.logs.length > 0) {
            data.logs.forEach(log => {
                appendLogLine(log);
                if (log.id > lastLogId) {
                    lastLogId = log.id;
                }
            });
        }
    } catch (e) {}
}

function appendLogLine(log) {
    const line = document.createElement("div");
    line.className = `log-line log-${log.level}`;
    line.innerHTML = `
        <span class="log-ts">[${log.timestamp}]</span>
        <span class="log-tag tag-${log.level}">${log.level}</span>
        <span class="log-msg">${escapeHtml(log.message)}</span>
    `;
    terminalLogs.appendChild(line);

    if (autoscrollChk.checked) {
        terminalLogs.scrollTop = terminalLogs.scrollHeight;
    }
}

// Toast helper
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
