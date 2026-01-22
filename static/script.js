function appendMessage(text, sender) {
    const log = document.getElementById('chat-log');
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.innerText = text;
    log.appendChild(msgDiv);
    log.scrollTop = log.scrollHeight;
}

async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        
        // Update Grid Stats
        document.getElementById('stat-found').innerText = data.stats.items_found;
        document.getElementById('stat-recycled').innerText = data.stats.recycled;
        document.getElementById('stat-toxic').innerText = data.stats.toxic;
        
        // Update Status
        const statusEl = document.getElementById('robot-status');
        const dotEl = document.querySelector('.status-dot');
        const toggleBtn = document.getElementById('toggle-btn');
        
        if (data.status === 'Active') {
            statusEl.innerText = "ONLINE - SCANNING";
            statusEl.style.color = "var(--primary)";
            dotEl.classList.remove('standby');
            toggleBtn.innerText = "STANDBY";
        } else {
            statusEl.innerText = "STANDBY MODE";
            statusEl.style.color = "var(--danger)";
            dotEl.classList.add('standby');
            toggleBtn.innerText = "ACTIVATE";
        }

        // Update Detection Label
        const detectionLabel = document.getElementById('detection-label');
        if (data.detected) {
            detectionLabel.innerText = "TARGET: " + data.detected.toUpperCase();
            detectionLabel.style.borderColor = "var(--primary)";
            detectionLabel.style.color = "var(--primary)";
        } else {
            detectionLabel.innerText = "SEARCHING...";
            detectionLabel.style.borderColor = "var(--text-muted)";
            detectionLabel.style.color = "var(--text-muted)";
        }

    } catch (err) {
        console.error("Error fetching stats:", err);
    }
}

async function toggleStatus() {
    try {
        const res = await fetch('/api/toggle');
        const data = await res.json();
        fetchStats(); // Update UI immediately
        // Also reload image if turning on? Video stream handles it.
    } catch (err) {
        console.error("Error toggling status:", err);
    }
}

async function analyze() {
    appendMessage("Analyzing current view...", "user");
    try {
        const res = await fetch('/api/analyze', { method: 'POST' });
        const data = await res.json();
        appendMessage(data.advice, "bot");
        fetchStats();
    } catch (err) {
        appendMessage("Error analyzing.", "bot");
    }
}

async function sendChat() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    appendMessage(text, "user");
    input.value = "";

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        appendMessage(data.response, "bot");
    } catch (err) {
        appendMessage("Error talking to advisor.", "bot");
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    setInterval(fetchStats, 1000); // Poll every second
    
    document.getElementById('toggle-btn').addEventListener('click', toggleStatus);
    document.getElementById('analyze-btn').addEventListener('click', analyze);
    document.getElementById('send-btn').addEventListener('click', sendChat);
    
    document.getElementById('chat-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChat();
    });
});
