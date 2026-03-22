# Stage 1: Build the frontend application
FROM node:20-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Stage 2: Serve the static files with a lightweight Nginx server
FROM nginx:1.27-alpine

# Update base packages to patch vulnerabilities
RUN apk update && apk upgrade && rm -rf /var/cache/apk/*

# Copy custom Nginx config with security headers
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built frontend from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Create non-root user for Nginx
RUN addgroup -g 101 -S nginx && \
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx

# Switch to non-root user
USER nginx

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]