#!/usr/bin/env python3
"""
  DUNGEON OF THE FORGOTTEN KING — Web Server
  Runs the game in a browser via xterm.js + WebSockets + PTY.
  Usage: python3 server.py [port]
"""

import fcntl
import os
import pty
import select
import struct
import subprocess
import termios
import threading
from pathlib import Path

from flask import Flask
from flask_sock import Sock

GAME_PATH = Path(__file__).parent / "dungeon_game.py"

app = Flask(__name__)
sock = Sock(app)

# ─────────────────────────────────────────────────────────────────────────────
# Frontend
# ─────────────────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Dungeon of the Forgotten King</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css"/>
  <style>
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      background: #000;
      display: flex;
      flex-direction: column;
      height: 100dvh;
      overflow: hidden;
    }

    #header {
      background: #0d0d0d;
      border-bottom: 1px solid #1a1a1a;
      color: #555;
      padding: 7px 16px;
      font-family: "Courier New", monospace;
      font-size: 11px;
      letter-spacing: 0.15em;
      text-align: center;
      flex-shrink: 0;
      user-select: none;
    }
    #header span { color: #997700; }

    #terminal-container {
      flex: 1;
      padding: 10px;
      overflow: hidden;
      min-height: 0;
    }

    #terminal { height: 100%; }
    .xterm-viewport { overflow-y: hidden !important; }

    /* Overlay */
    #overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.92);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      gap: 20px;
      z-index: 100;
    }
    #overlay.hidden { display: none; }

    #overlay .title {
      font-family: "Courier New", monospace;
      color: #997700;
      font-size: clamp(11px, 2vw, 14px);
      letter-spacing: 0.2em;
      text-align: center;
      white-space: pre;
      line-height: 1.4;
    }

    #overlay .subtitle {
      font-family: "Courier New", monospace;
      color: #444;
      font-size: 12px;
      letter-spacing: 0.1em;
    }

    #start-btn {
      background: transparent;
      color: #888;
      border: 1px solid #333;
      padding: 12px 36px;
      font-family: "Courier New", monospace;
      font-size: 13px;
      letter-spacing: 0.2em;
      cursor: pointer;
      transition: all 0.15s;
    }
    #start-btn:hover {
      background: #111;
      color: #ccc;
      border-color: #666;
    }
  </style>
</head>
<body>

<div id="header">⚔ &nbsp; <span>DUNGEON OF THE FORGOTTEN KING</span> &nbsp; ⚔</div>
<div id="terminal-container">
  <div id="terminal"></div>
</div>

<div id="overlay">
  <div class="title">██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗
██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║
██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║
██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║
██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║
╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝</div>
  <div class="subtitle">of the &nbsp; F O R G O T T E N &nbsp; K I N G</div>
  <button id="start-btn">ENTER THE DUNGEON</button>
</div>

<script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js"></script>
<script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>
<script>
const overlay  = document.getElementById('overlay');
const startBtn = document.getElementById('start-btn');

const term = new Terminal({
  cursorBlink: true,
  allowProposedApi: true,
  fontFamily: '"Cascadia Code", "Fira Code", "Courier New", monospace',
  fontSize: window.innerWidth < 600 ? 12 : 14,
  lineHeight: 1.2,
  theme: {
    background:    '#000000',
    foreground:    '#cccccc',
    cursor:        '#888888',
    black:         '#000000',
    red:           '#cc4444',
    green:         '#44aa44',
    yellow:        '#aaaa44',
    blue:          '#6666cc',
    magenta:       '#aa44aa',
    cyan:          '#44aaaa',
    white:         '#cccccc',
    brightBlack:   '#555555',
    brightRed:     '#ff6666',
    brightGreen:   '#66dd66',
    brightYellow:  '#dddd66',
    brightBlue:    '#8888ff',
    brightMagenta: '#dd66dd',
    brightCyan:    '#66dddd',
    brightWhite:   '#ffffff',
  },
});

const fitAddon = new FitAddon.FitAddon();
term.loadAddon(fitAddon);
term.open(document.getElementById('terminal'));
fitAddon.fit();

let ws = null;

function sendResize() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(`\x00RESIZE:${term.cols}:${term.rows}`);
  }
}

window.addEventListener('resize', () => {
  fitAddon.fit();
  sendResize();
});

function connect() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/ws`);

  ws.onopen = () => {
    overlay.classList.add('hidden');
    term.reset();
    term.focus();
    sendResize();
  };

  ws.onmessage = (e) => {
    term.write(e.data);
  };

  ws.onclose = () => {
    term.write('\r\n\r\n\x1b[2m  [Session ended. Press the button to play again.]\x1b[0m\r\n');
    overlay.classList.remove('hidden');
    overlay.querySelector('.subtitle').textContent = 'of the  F O R G O T T E N  K I N G';
    startBtn.textContent = 'PLAY AGAIN';
  };

  term.onData((data) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(data);
    }
  });
}

startBtn.addEventListener('click', () => {
  if (ws) { ws.close(); ws = null; }
  connect();
});
</script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# PTY helpers
# ─────────────────────────────────────────────────────────────────────────────

def set_winsize(fd, rows, cols):
    s = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, s)


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return HTML


@sock.route("/ws")
def game_ws(ws):
    """
    Spawn one game process per WebSocket connection.
    Bridge: browser keystrokes → PTY stdin, PTY stdout → browser xterm.js.
    """
    master_fd, slave_fd = pty.openpty()
    set_winsize(master_fd, 24, 80)  # sensible default before browser reports size

    proc = subprocess.Popen(
        ["python3", "-u", str(GAME_PATH)],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        close_fds=True,
        env={
            **os.environ,
            "PYTHONUNBUFFERED": "1",
            "TERM": "xterm-256color",
            "COLUMNS": "80",
            "LINES": "24",
        },
    )
    os.close(slave_fd)

    stop = threading.Event()

    def pty_reader():
        """Read PTY output and forward to the browser."""
        while not stop.is_set():
            try:
                r, _, _ = select.select([master_fd], [], [], 0.05)
                if r:
                    data = os.read(master_fd, 4096)
                    ws.send(data.decode("utf-8", errors="replace"))
            except OSError:
                break
        stop.set()

    reader = threading.Thread(target=pty_reader, daemon=True)
    reader.start()

    try:
        while not stop.is_set() and proc.poll() is None:
            try:
                data = ws.receive(timeout=0.1)
                if data is None:
                    break
                # Control message: resize event from browser
                if data.startswith("\x00RESIZE:"):
                    _, cols, rows = data.split(":")
                    set_winsize(master_fd, int(rows), int(cols))
                else:
                    os.write(master_fd, data.encode())
            except Exception:
                break
    finally:
        stop.set()
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        try:
            os.close(master_fd)
        except OSError:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    # Cloud platforms inject $PORT; fall back to CLI arg or 5000
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 5000))
    print(f"\n  Dungeon of the Forgotten King — Web Server")
    print(f"  ─────────────────────────────────────────")
    print(f"  Local:   http://localhost:{port}")
    print(f"  Network: http://0.0.0.0:{port}")
    print(f"\n  Press Ctrl+C to stop.\n")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
