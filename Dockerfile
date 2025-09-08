FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copy pyproject.toml, uv.lock, and README.md first for better caching
COPY pyproject.toml uv.lock README.md ./

# Install dependencies with uv
RUN uv sync --frozen

# Copy source code
COPY . .

# Install the package in development mode
RUN uv pip install -e .

# Create data directory
RUN mkdir -p data/raw

# Make start script executable
RUN chmod +x start.py

# Create a non-root user
RUN useradd -m -u 1000 user
USER user

# Expose the port
EXPOSE 7860

# Set environment variables
ENV PANEL_ALLOW_WEBSOCKET_ORIGIN=*
ENV BOKEH_ALLOW_WS_ORIGIN=*
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Change ownership of the app directory
USER root
RUN chown -R user:user /app
USER user

# Run the application
CMD ["python", "start.py"]
