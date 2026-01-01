# Frontend Dockerfile (React + Vite)
FROM node:20-bullseye-slim
WORKDIR /app
# Copy package files from the frontend build context
# Copy only package.json so the container can install correct optional native packages for Linux
COPY package.json ./
# Ensure optional dependencies are allowed so native rollup binary for the container platform installs
ENV NPM_CONFIG_OPTIONAL=true
# Install dependencies inside the container (will create a package-lock.json appropriate for Linux)
RUN npm install --legacy-peer-deps
# Copy the rest of the frontend source
COPY . .
EXPOSE 5173
# Run vite bound to 0.0.0.0 so container is reachable from host
CMD ["npm", "run", "dev", "--", "--host"]
