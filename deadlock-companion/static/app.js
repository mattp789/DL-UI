const RECONNECT_DELAY = 2000;

let ws = null;
let objectives = [];

function connect() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onopen = () => {
        document.getElementById("status-indicator").className = "connected";
        document.getElementById("status-text").textContent = "Connected";
    };

    ws.onclose = () => {
        document.getElementById("status-indicator").className = "disconnected";
        document.getElementById("status-text").textContent = "Disconnected";
        setTimeout(connect, RECONNECT_DELAY);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleUpdate(data);
    };
}

function handleUpdate(data) {
    const matchState = data.match_state;
    document.getElementById("match-state").textContent =
        matchState === "active" ? "Match Active" : "Idle";

    const waitingOverlay = document.getElementById("waiting-overlay");
    if (matchState === "idle") {
        waitingOverlay.classList.remove("hidden");
    } else {
        waitingOverlay.classList.add("hidden");
    }

    objectives = data.objectives;
    renderMarkers();
}

function renderMarkers() {
    const container = document.getElementById("markers");
    container.innerHTML = "";

    for (const obj of objectives) {
        const marker = document.createElement("div");
        marker.className = `marker ${getStateClass(obj)}`;
        marker.dataset.type = obj.type;

        marker.style.left = `${obj.position[0] * 100}%`;
        marker.style.top = `${obj.position[1] * 100}%`;

        const tooltip = document.createElement("div");
        tooltip.className = "tooltip";
        tooltip.textContent = obj.name;
        marker.appendChild(tooltip);

        if (obj.remaining_seconds != null) {
            const label = document.createElement("div");
            label.className = "timer-label";
            label.textContent = formatTime(obj.remaining_seconds);
            marker.appendChild(label);
        }

        const icons = {
            t1_camp: "1",
            t2_camp: "2",
            t3_camp: "3",
            sinner: "S",
            bridge_buff: "B",
        };
        marker.insertBefore(
            document.createTextNode(icons[obj.type] || "?"),
            marker.firstChild
        );

        marker.addEventListener("contextmenu", (e) => {
            e.preventDefault();
            toggleObjective(obj.id);
        });

        container.appendChild(marker);
    }
}

function getStateClass(obj) {
    if (obj.state === "alive") return "alive";
    if (obj.remaining_seconds == null) return "alive";

    const ratio = obj.remaining_seconds / obj.respawn_total;

    if (obj.remaining_seconds <= 15) return "respawning-soon";
    if (ratio > 0.75) return "dead-full";
    if (ratio > 0.5) return "dead-high";
    return "dead-low";
}

function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
}

function toggleObjective(id) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "toggle", id: id }));
    }
}

document.getElementById("recalibrate-btn").addEventListener("click", () => {
    fetch("/api/recalibrate", { method: "POST" });
});

async function pollState() {
    try {
        const resp = await fetch("/api/state");
        const data = await resp.json();
        handleUpdate(data);
    } catch (e) {
        // Server not ready yet
    }
}

pollState();
connect();
