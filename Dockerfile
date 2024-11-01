# Use an official Python runtime as a parent image
FROM python:3.11.7-slim
  
# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl=7.* && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash appuser

# Set the working directory in the container
WORKDIR /app

# Copy files first
COPY . .

# Set correct ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Install dependencies as non-root user
RUN pip install --no-cache-dir --user -r requirements.txt
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copy the current directory contents into the container at /app
COPY . .

# Make port configurable via environment variable
ENV PORT=8501

# Expose the port
EXPOSE $PORT

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f "http://localhost:${PORT}/_stcore/health" -H "Accept: application/json" || exit 1

# Run app.py when the container launches with the specified port
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["streamlit run app.py --server.port $PORT --server.address=0.0.0.0 --server.headless=true"]
