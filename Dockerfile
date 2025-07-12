# Use official Python image
FROM python:3.12

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose port (default Django runserver port)
EXPOSE 8000

# Set environment variables (optional, for better practice)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Start server (entrypoint for local dev)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
