# Use official Python image
FROM python:3.12-slim

# Install Linux packages (including tesseract OCR)
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy project files
COPY . .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port (Railway uses 8080)
EXPOSE 8080

# Start Django app with gunicorn
CMD ["gunicorn", "homexbackend.wsgi.application", "-b", "0.0.0.0:8080"]
