FROM nginx:latest

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Remove all default nginx configs
RUN rm -rf /etc/nginx/conf.d/* && \
    rm -f /etc/nginx/nginx.conf

# Create fresh nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Create directory for our config and ensure it's writable
RUN mkdir -p /etc/nginx/conf.d && \
    chmod 755 /etc/nginx/conf.d

# Copy our config
COPY ssl.conf /etc/nginx/conf.d/default.conf

# Set proper permissions
RUN chmod 644 /etc/nginx/conf.d/default.conf