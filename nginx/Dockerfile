FROM nginx:latest

RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* 

# Create necessary directories
RUN mkdir -p /etc/nginx/conf.d

# Copy SSL configuration
COPY ssl.conf /etc/nginx/conf.d/ssl.conf

# Make sure the file has proper permissions
RUN chmod 644 /etc/nginx/conf.d/ssl.conf