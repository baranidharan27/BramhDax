# Use official Python image as a base
FROM python:3.10-slim


# Set working directory inside the container
WORKDIR /app

# Install uv (dependency manager)
RUN pip install uv 

# Copy the requirements file into the container
COPY . .

# Install dependencies from requirements file using uv
RUN uv pip install --system -r requirements.txt


# Run the main pipeline when the container starts
CMD [ "python", "main.py"]

# Expose the port the app runs on
EXPOSE 8000 b
# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app     