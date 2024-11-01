# Use an official Python runtime as a parent image
FROM python:3.11.7-slim
  
# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl=7.* && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash appuser
USER appuser

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port", "--server.address=0.0.0.0", "--server.headless=true"]
CMD ["/bin/sh", "-c", "echo $PORT"]
