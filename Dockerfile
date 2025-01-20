# Use Google Cloud SDK's container as the base image
FROM google/cloud-sdk:latest

# Specify your email address as the maintainer of the container image
LABEL maintainer="peravali@pdx.edu"

# Copy the contents of the current directory into the container directory /app
COPY . /app

# Set the working directory of the container to /app
WORKDIR /app

# Install necessary packages
RUN apt-get update -y && apt-get install -y python3-pip python3-venv \
    && python3 -m venv /env && /env/bin/pip install --no-cache-dir Flask google-cloud-datastore gunicorn requests

# Set the PATH to use the virtual environment's Python and pip
ENV PATH="/env/bin:$PATH"

# set the Google Cloud credentials file
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json

# Expose the port the app runs on
EXPOSE 5000

# Set the parameters to the program
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app

