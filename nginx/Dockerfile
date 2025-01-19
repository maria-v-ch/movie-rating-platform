FROM nginx:latest

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Create directory for our config
RUN mkdir -p /etc/nginx/conf.d

# Copy our config
COPY ssl.conf /etc/nginx/conf.d/default.conf

# Set proper permissions
RUN chmod 644 /etc/nginx/conf.d/default.conf