# VizDoom Player Container
# Headless game environment with Xvfb virtual framebuffer and noVNC web viewer
#
# Ports:
#   6901 - noVNC web viewer
#   5900 - VNC (raw)
#   50051 - gRPC agent communication

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV VNC_PORT=5900
ENV NOVNC_PORT=6901
ENV GRPC_PORT=50051

# System dependencies for VizDoom + display + networking
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools required by VizDoom
    cmake \
    g++ \
    make \
    # Boost libraries for VizDoom
    libboost-all-dev \
    # OpenGL / rendering
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libsdl2-dev \
    # Virtual framebuffer
    xvfb \
    # VNC server
    x11vnc \
    # noVNC + websockify
    novnc \
    websockify \
    # Python 3.11
    python3.11 \
    python3.11-venv \
    python3-pip \
    # Misc
    wget \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set python3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install VizDoom and gRPC dependencies
RUN pip3 install --no-cache-dir \
    vizdoom==1.2.3 \
    grpcio==1.62.3 \
    grpcio-tools==1.62.3 \
    protobuf==4.25.5 \
    numpy==1.26.4 \
    duckdb==1.1.3 \
    scipy==1.12.0 \
    statsmodels==0.14.4 \
    matplotlib==3.8.5

# Verify VizDoom installation and scenario availability
RUN python3 -c "import vizdoom; print('VizDoom version:', vizdoom.__version__); print('Scenarios path:', vizdoom.scenarios_path)"

WORKDIR /app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE ${VNC_PORT} ${NOVNC_PORT} ${GRPC_PORT}

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD pgrep -x Xvfb > /dev/null || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
