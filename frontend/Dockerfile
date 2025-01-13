# Build stage
FROM node:20-alpine as build

# Set npm registry to use a faster mirror
RUN npm config set registry https://registry.npmmirror.com/

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with retries and increased timeout
RUN apk add --no-cache git && \
    npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 100000 && \
    npm config set fetch-retry-maxtimeout 600000 && \
    npm install --legacy-peer-deps && \
    npm install --save-dev @babel/plugin-proposal-private-property-in-object

# Copy project files
COPY . .

# Clean npm cache and rebuild node-sass
RUN npm cache clean --force && \
    npm rebuild node-sass

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
