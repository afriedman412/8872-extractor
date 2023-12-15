# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy your project files into the container
COPY . /app

# Copy the Poetry configuration files and install dependencies
RUN pip install -r requirements.txt

# Expose the port your app will run on (if needed)
EXPOSE 5000

# Define the command to run your application
CMD ["python", "app.py"]
