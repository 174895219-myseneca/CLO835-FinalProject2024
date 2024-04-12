FROM ubuntu:20.04

# Install dependencies
RUN apt-get update -y && \
    apt-get install -y python3-pip mysql-client && \
    pip install --upgrade pip

# Copy application source
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install -r requirements.txt

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_SESSION_TOKEN
ARG S3_BUCKET_URL

# Set the AWS credentials and S3 bucket URL as environment variables
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \  
    S3_BUCKET_URL=$S3_BUCKET_URL

EXPOSE 8080

# Run the application
ENTRYPOINT ["python3"]
CMD ["app.py"]