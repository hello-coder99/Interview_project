const packetTable = document.querySelector("#packetTable");
const filterInput = document.querySelector("#filterInput");
const pauseButton = document.querySelector("#pauseButton");
const clearButton = document.querySelector("#clearButton");
const exportButton = document.querySelector("#exportButton");
const statusPill = document.querySelector("#statusPill");
const statusText = document.querySelector("#statusText");

const counters = {
  total: document.querySelector("#totalCount"),
  tcp: document.querySelector("#tcpCount"),
  udp: document.querySelector("#udpCount"),
  other: document.querySelector("#otherCount"),
};

let packets = [];
let paused = false;
let socket;
let reconnectTimer;

function protocolClass(protocol) {
  const value = String(protocol || "OTHER").toLowerCase();
  if (value === "tcp" || value === "udp") {
    return value;
  }
  return "other";
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => (
    {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    }[char]
  ));
}

function filteredPackets() {
  const query = filterInput.value.trim().toLowerCase();
  if (!query) {
    return packets;
  }

  return packets.filter((packet) => (
    packet.src_ip.toLowerCase().includes(query)
    || packet.dst_ip.toLowerCase().includes(query)
    || packet.protocol.toLowerCase().includes(query)
  ));
}

function renderTable() {
  const visiblePackets = filteredPackets();
  if (visiblePackets.length === 0) {
    packetTable.innerHTML = '<tr class="empty-row"><td colspan="4">No packets match the current view.</td></tr>';
    return;
  }

  packetTable.innerHTML = visiblePackets
    .slice()
    .reverse()
    .map((packet) => {
      const protocol = escapeHtml(packet.protocol || "OTHER");
      return `
        <tr>
          <td>${escapeHtml(packet.captured_at || "")}</td>
          <td>${escapeHtml(packet.src_ip)}</td>
          <td>${escapeHtml(packet.dst_ip)}</td>
          <td><span class="protocol ${protocolClass(protocol)}">${protocol}</span></td>
        </tr>
      `;
    })
    .join("");
}

function renderCounters() {
  const counts = packets.reduce((acc, packet) => {
    const protocol = protocolClass(packet.protocol);
    acc.total += 1;
    acc[protocol] += 1;
    return acc;
  }, { total: 0, tcp: 0, udp: 0, other: 0 });

  counters.total.textContent = counts.total;
  counters.tcp.textContent = counts.tcp;
  counters.udp.textContent = counts.udp;
  counters.other.textContent = counts.other;
}

function render() {
  renderCounters();
  renderTable();
}

function addPacket(packet) {
  packets.push({
    src_ip: packet.src_ip || "",
    dst_ip: packet.dst_ip || "",
    protocol: packet.protocol || "OTHER",
    captured_at: packet.captured_at || new Date().toLocaleTimeString(),
  });

  if (packets.length > 500) {
    packets = packets.slice(-500);
  }

  if (!paused) {
    render();
  }
}

function setStatus(connected, message) {
  statusPill.classList.toggle("connected", connected);
  statusText.textContent = message;
}

function connectSocket() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${protocol}://${window.location.host}/ws/packets`);

  socket.addEventListener("open", () => {
    setStatus(true, "Dashboard connected");
  });

  socket.addEventListener("message", (event) => {
    addPacket(JSON.parse(event.data));
  });

  socket.addEventListener("close", () => {
    setStatus(false, "Dashboard reconnecting");
    clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(connectSocket, 1500);
  });
}

async function refreshStatus() {
  try {
    const response = await fetch("/api/status");
    const status = await response.json();
    setStatus(status.connected, status.message);
  } catch {
    setStatus(false, "FastAPI server unavailable");
  }
}

function exportCsv() {
  const rows = [["Time", "Source IP", "Destination IP", "Protocol"], ...filteredPackets().map((packet) => [
    packet.captured_at,
    packet.src_ip,
    packet.dst_ip,
    packet.protocol,
  ])];
  const csv = rows.map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "packets.csv";
  link.click();
  URL.revokeObjectURL(url);
}

filterInput.addEventListener("input", renderTable);
clearButton.addEventListener("click", () => {
  packets = [];
  render();
});
pauseButton.addEventListener("click", () => {
  paused = !paused;
  pauseButton.textContent = paused ? "Resume" : "Pause";
  if (!paused) {
    render();
  }
});
exportButton.addEventListener("click", exportCsv);

connectSocket();
refreshStatus();
setInterval(refreshStatus, 2000);
