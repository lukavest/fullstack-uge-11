FROM python:3.11-slim

WORKDIR /app

# Copy frontend files
COPY . .

# Expose port
EXPOSE 3000

# Serve files using Python's built-in HTTP server
CMD ["python", "-m", "http.server", "3000"]
