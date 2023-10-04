# Use the official Python image as the base image
FROM python:3.8

# Set environment variables for Python to run in unbuffered mode (recommended for Docker)
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install any required dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /app/

# Expose port 8000 (or the port you want to use)
EXPOSE 8000

# Command to run the application (modify this based on how you run your FastAPI app)
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]