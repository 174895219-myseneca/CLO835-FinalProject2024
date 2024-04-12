FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends default-mysql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
EXPOSE 81

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
