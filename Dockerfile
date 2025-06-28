# To deploy use gcloud builds submit --config=cloudbuild.yaml .


# Use an official Python runtime as a parent image
FROM python:3.11.3-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install dependencies (including the Git-based package)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV PORT=8080

# Run app.py when the container launches
CMD ["gunicorn", "-b", ":8080", "app:app"]
