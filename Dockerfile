# # Build Stage: Install Dependencies in an Isolated Environment
# FROM python:3.9-slim AS builder

# # Set working directory
# WORKDIR /src

# # Copy only the requirements file first for caching optimization
# COPY requirements.txt .

# # Install dependencies globally
# RUN pip install --no-cache-dir -r requirements.txt

# # Final Runtime Stage: Minimal Image with Only the Essentials
# FROM python:3.9-slim

# # Set working directory
# WORKDIR /src

# # Copy installed dependencies from the builder stage
# COPY --from=builder /usr/local /usr/local

# # ✅ Copy only the `src/` directory instead of everything
# COPY src /src

# # ✅ Set PYTHONPATH so `src/` is recognized as a module
# ENV PYTHONPATH="/src"

# # Create a non-root user for security
# RUN useradd -m appuser && chown -R appuser /src

# # Switch to non-root user
# USER appuser

# # Environment variables for Vault integration (set dynamically in Docker Compose)
# ENV VAULT_ADDR=http://vault:8200
# ENV VAULT_TOKEN=root

# # Run the application
# CMD ["python", "main.py"]
# ---- Stage 1: Builder Image to Install Dependencies ----
FROM python:3.9-slim AS builder

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (only needed for certain Python packages)
RUN apt-get update && apt-get install -y gcc libffi-dev && rm -rf /var/lib/apt/lists/*

# ✅ Copy only `requirements.txt` first to enable caching
COPY requirements.txt .

# ✅ Install dependencies in a dedicated location to keep the final image clean
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: Final Minimal Image ----
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# ✅ Copy installed dependencies from the builder stage
COPY --from=builder /install /usr/local

# ✅ Copy the actual application source code (fix for missing files)
COPY src /app/src

# ✅ Set PYTHONPATH so `src/` is recognized as a module
ENV PYTHONPATH="/app/src"

# ✅ Create a non-root user for security
RUN useradd -m appuser && chown -R appuser /app

# ✅ Switch to the non-root user
USER appuser

# ✅ Run the application in module mode to ensure correct imports
CMD ["python", "-m", "src.main"]
    