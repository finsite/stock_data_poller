# Use a lightweight base image (e.g., Alpine)
FROM alpine:latest

# Set working directory
WORKDIR /app

# Copy application files (this can be customized later based on your app)
COPY . /app

# Install dependencies (if needed)
RUN apk update && apk add --no-cache curl

# Default command (this is just a placeholder and should be customized later)
CMD ["echo", "Hello from the generic Kubernetes app!"]
