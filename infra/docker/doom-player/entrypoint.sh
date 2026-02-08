#!/usr/bin/env bash
set -euo pipefail

DISPLAY="${DISPLAY:-:99}"
VNC_PORT="${VNC_PORT:-5900}"
NOVNC_PORT="${NOVNC_PORT:-6901}"
SCREEN_RESOLUTION="${SCREEN_RESOLUTION:-640x480x24}"

echo "[doom-player] Starting Xvfb on display ${DISPLAY} (${SCREEN_RESOLUTION})"
Xvfb "${DISPLAY}" -screen 0 "${SCREEN_RESOLUTION}" -ac +extension GLX &
XVFB_PID=$!

# Wait for Xvfb to be ready
sleep 1
if ! kill -0 "${XVFB_PID}" 2>/dev/null; then
    echo "[doom-player] ERROR: Xvfb failed to start"
    exit 1
fi
echo "[doom-player] Xvfb running (PID: ${XVFB_PID})"

export DISPLAY

echo "[doom-player] Starting x11vnc on port ${VNC_PORT}"
x11vnc -display "${DISPLAY}" -rfbport "${VNC_PORT}" -nopw -shared -forever -noxdamage -bg
echo "[doom-player] x11vnc running"

echo "[doom-player] Starting noVNC websockify on port ${NOVNC_PORT} -> ${VNC_PORT}"
websockify --web /usr/share/novnc "${NOVNC_PORT}" "localhost:${VNC_PORT}" &
NOVNC_PID=$!
echo "[doom-player] noVNC running (PID: ${NOVNC_PID})"

echo "[doom-player] Infrastructure ready."
echo "[doom-player]   VNC:   vnc://localhost:${VNC_PORT}"
echo "[doom-player]   noVNC: http://localhost:${NOVNC_PORT}/vnc.html"

# If arguments passed, execute them (e.g. python3 glue/vizdoom_bridge.py)
if [ $# -gt 0 ]; then
    echo "[doom-player] Executing command: $*"
    exec "$@"
fi

# Otherwise keep container alive waiting for external commands
echo "[doom-player] Waiting for commands..."
wait "${XVFB_PID}"
