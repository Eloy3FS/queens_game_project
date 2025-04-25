# Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code
COPY . .

# Expose the port that Gunicorn will bind to
EXPOSE 7860

# Run the Flask app via Gunicorn on 0.0.0.0:7860
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:7860", "--workers", "1", "--threads", "4"]
