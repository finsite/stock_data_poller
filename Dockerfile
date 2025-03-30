# ---- Stage 1: Builder Image ----
    FROM python:3.9-slim AS builder

    WORKDIR /app
    
    # # Install system dependencies (only if needed for certain packages)
    RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        gcc=4:10.2.1-1 \
        libffi-dev=3.3-6 && \
    rm -rf /var/lib/apt/lists/*

    # ✅ Copy only `requirements.txt` first for caching optimization
    COPY requirements.txt .
    
    # ✅ Install dependencies in an isolated directory (avoids polluting the final image)
    RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
    
    # ---- Stage 2: Minimal Final Image ----
    FROM python:3.9-slim
    
    WORKDIR /app
    
    # ✅ Copy installed dependencies from the builder stage
    COPY --from=builder /install /usr/local
    
    # ✅ Copy the application source code explicitly
    COPY src /app/src
    
    # ✅ Set PYTHONPATH so `src/` is recognized inside the container
    ENV PYTHONPATH="/app/src"
    
    # ✅ Create a non-root user for security
    RUN useradd -m appuser && chown -R appuser /app
    
    # ✅ Switch to the non-root user
    USER appuser
    
    # ✅ Run `main.py` directly instead of using module mode
    CMD ["python", "/app/src/main.py"]
    
