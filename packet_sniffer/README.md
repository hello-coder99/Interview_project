# Packet Sniffer Web Dashboard

This project keeps the existing C++ raw socket sniffer and replaces the Tkinter dashboard with a FastAPI web dashboard.

## Files

- `sniffer.cpp` captures packets, prints protocol details, optionally saves `capture.pcap`, and streams packet summaries as newline-delimited JSON on TCP port `9090`.
- `dashboard.py` runs the FastAPI server, connects to the C++ sniffer feed, stores recent packets, and broadcasts live updates to the browser through WebSockets.
- `templates/index.html`, `static/styles.css`, and `static/app.js` provide the web UI.

## Setup

```bash
pip install -r requirements.txt
g++ sniffer.cpp -o sniffer
```

Raw packet capture usually requires Linux and elevated privileges.

## Run

Start the web dashboard first:

```bash
uvicorn dashboard:app --reload --host 127.0.0.1 --port 8000
```

In another terminal, start the sniffer:

```bash
sudo ./sniffer
```

When prompted, choose GUI support:

```text
Do you want to save the file (Y=1/N=0):0
Do you want gui support (Y=1/N=0):1
```

Open `http://127.0.0.1:8000` in a browser.
