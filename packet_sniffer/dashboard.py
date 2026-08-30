import asyncio
import json
import socket
import threading
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
SNIFFER_HOST = "127.0.0.1"
SNIFFER_PORT = 9090
MAX_HISTORY = 500

app = FastAPI(title="Packet Analyzer Dashboard")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

packet_history: list[dict[str, Any]] = []
connected_clients: set[WebSocket] = set()
state_lock = threading.Lock()
stop_event = threading.Event()
sniffer_socket: socket.socket | None = None
packet_queue: asyncio.Queue[dict[str, Any]] | None = None
broadcast_task: asyncio.Task | None = None
reader_thread: threading.Thread | None = None
main_loop: asyncio.AbstractEventLoop | None = None

connection_state = {
    "connected": False,
    "message": "Waiting for sniffer on 127.0.0.1:9090",
    "last_packet_at": None,
}


def update_connection_state(connected: bool, message: str) -> None:
    with state_lock:
        connection_state["connected"] = connected
        connection_state["message"] = message


def remember_packet(packet: dict[str, Any]) -> dict[str, Any]:
    enriched = {
        "src_ip": packet.get("src_ip", ""),
        "dst_ip": packet.get("dst_ip", ""),
        "protocol": packet.get("protocol", "OTHER"),
        "captured_at": time.strftime("%H:%M:%S"),
    }
    with state_lock:
        packet_history.append(enriched)
        if len(packet_history) > MAX_HISTORY:
            del packet_history[: len(packet_history) - MAX_HISTORY]
        connection_state["last_packet_at"] = enriched["captured_at"]
    return enriched


def socket_reader() -> None:
    global sniffer_socket

    while not stop_event.is_set():
        try:
            update_connection_state(False, f"Connecting to sniffer on {SNIFFER_HOST}:{SNIFFER_PORT}")
            client = socket.create_connection((SNIFFER_HOST, SNIFFER_PORT), timeout=3)
            sniffer_socket = client
            update_connection_state(True, "Connected to sniffer")

            with client:
                buffer = ""
                while not stop_event.is_set():
                    data = client.recv(4096)
                    if not data:
                        break

                    buffer += data.decode("utf-8", errors="replace")
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if not line.strip():
                            continue

                        try:
                            packet = remember_packet(json.loads(line))
                        except json.JSONDecodeError:
                            continue

                        if main_loop and packet_queue:
                            main_loop.call_soon_threadsafe(packet_queue.put_nowait, packet)
        except OSError:
            update_connection_state(False, f"Sniffer unavailable on {SNIFFER_HOST}:{SNIFFER_PORT}")
            stop_event.wait(2)
        finally:
            sniffer_socket = None
            if not stop_event.is_set():
                update_connection_state(False, "Sniffer disconnected; retrying")


async def broadcast_packets() -> None:
    assert packet_queue is not None

    while True:
        packet = await packet_queue.get()
        stale_clients: list[WebSocket] = []

        for websocket in list(connected_clients):
            try:
                await websocket.send_json(packet)
            except RuntimeError:
                stale_clients.append(websocket)

        for websocket in stale_clients:
            connected_clients.discard(websocket)


@app.on_event("startup")
async def startup() -> None:
    global broadcast_task, main_loop, packet_queue, reader_thread

    main_loop = asyncio.get_running_loop()
    packet_queue = asyncio.Queue()
    stop_event.clear()
    broadcast_task = asyncio.create_task(broadcast_packets())
    reader_thread = threading.Thread(target=socket_reader, daemon=True)
    reader_thread.start()


@app.on_event("shutdown")
async def shutdown() -> None:
    stop_event.set()
    if sniffer_socket:
        sniffer_socket.close()
    if broadcast_task:
        broadcast_task.cancel()


@app.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    return (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")


@app.get("/api/status")
async def status() -> dict[str, Any]:
    with state_lock:
        return {
            **connection_state,
            "stored_packets": len(packet_history),
            "browser_clients": len(connected_clients),
        }


@app.get("/api/packets")
async def packets() -> list[dict[str, Any]]:
    with state_lock:
        return list(packet_history)


@app.websocket("/ws/packets")
async def packet_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    connected_clients.add(websocket)

    with state_lock:
        history = list(packet_history)

    for packet in history:
        await websocket.send_json(packet)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
