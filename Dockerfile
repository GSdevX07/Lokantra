FROM python:3.11-slim

# Install system dependencies for OpenCV and builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy uv from official uv image
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# Create non-root user (Hugging Face default UID 1000)
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /app/backend

# Copy backend dependency files first for caching
COPY backend/pyproject.toml backend/uv.lock ./

# Install Python dependencies with uv
RUN uv sync --frozen

# Copy backend source code
COPY backend/ /app/backend/

# Ensure uploads and logs directories exist and are owned by user
RUN mkdir -p /app/backend/uploads /app/backend/logs /app/backend/uploads/simulations \
    && chown -R user:user /app

USER user

# Hugging Face Spaces exposes port 7860
ENV PORT=7860
ENV FLASK_PORT=7860
ENV FLASK_HOST=0.0.0.0
EXPOSE 7860

# Run Flask backend
CMD ["uv", "run", "python", "run.py"]
