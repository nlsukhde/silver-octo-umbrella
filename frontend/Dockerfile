# Use an official Node runtime as a parent image
FROM node:14

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install any needed packages
RUN npm install

# Bundle app source
COPY . .

# Build your app
RUN npm run build

# Install a simple server for serving static content
RUN npm install -g serve

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run serve when the container launches
CMD ["serve", "-s", "build", "-l", "3000"]
