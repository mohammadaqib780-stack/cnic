# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr libsm6 libxext6 libxrender-dev && \
    pip install --upgrade pip

# Copy project
WORKDIR /app
COPY . /app

# Install python dependencies
RUN pip install -r requirements.txt

# Collect static if needed
RUN python manage.py collectstatic --noinput

# Run server
CMD ["gunicorn", "your_project_name.wsgi:application", "--bind", "0.0.0.0:8000"]
