FROM ubuntu:20.04

# Install dependencies
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev mysql-client && \
    pip install --upgrade pip

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy application source
COPY app.py ./
COPY templates/ templates/

EXPOSE 81

# Run the application
ENTRYPOINT ["python3"]
CMD ["app.py"]
