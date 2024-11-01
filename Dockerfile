# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port configurable via environment variable
ENV PORT=8501

# Expose the port
EXPOSE $PORT

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/_stcore/health || exit 1

# Run app.py when the container launches with the specified port
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port"]
CMD ["8501"]