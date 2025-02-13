# Build Stage: Install Dependencies in an Isolated Environment
FROM python:3.9-slim AS builder

# Set working directory
WORKDIR /src

# Copy only the requirements file first for caching optimization
COPY requirements.txt .

# Install dependencies globally
RUN pip install --no-cache-dir -r requirements.txt

# Final Runtime Stage: Minimal Image with Only the Essentials
FROM python:3.9-slim

# Set working directory
WORKDIR /src

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local /usr/local

# ✅ Copy only the `src/` directory instead of everything
COPY src /src

# ✅ Set PYTHONPATH so `src/` is recognized as a module
ENV PYTHONPATH="/src"

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser /src

# Switch to non-root user
USER appuser

# Environment variables for Vault integration (set dynamically in Docker Compose)
ENV VAULT_ADDR=http://vault:8200
ENV VAULT_TOKEN=root

# Run the application
CMD ["python", "main.py"]
