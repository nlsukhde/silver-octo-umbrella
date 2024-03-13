# Base image
FROM node:16-alpine as build

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./

RUN npm install

# Copy the rest of the application source code
COPY . .

# Build app
RUN npm run build

