/**
 * Configuration file for API endpoints
 * Supports both Docker and local development environments
 */

let API_BASE_URL = "http://localhost:8000";

// Detect if running in Docker based on hostname
if (window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
    // Running in Docker container
    API_BASE_URL = "http://backend:8000";
}

// Allow override via environment variable injected at runtime
if (window.API_BASE_URL) {
    API_BASE_URL = window.API_BASE_URL;
}

export { API_BASE_URL };
