# Use Node 22 as the base image for building the Angular app
FROM node:22-alpine as build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Angular app for production
RUN npm run build --configuration=production

# Use Nginx as the reverse proxy to serve the built files
FROM nginx:alpine

# Copy the build output to replace the default nginx contents
COPY --from=build /app/dist/resumecraft-ui/browser /usr/share/nginx/html

# Copy the custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]
