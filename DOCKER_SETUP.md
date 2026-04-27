# Docker Setup Guide - Grill Chef

This guide will help you set up and run the Grill Chef application using Docker.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- Docker Compose (usually included with Docker Desktop)

## Quick Start

### 1. Build and Run the Application

From the project root directory, run:

```bash
docker-compose up --build
```

This command will:
- Build the backend Docker image
- Build the frontend Docker image
- Start both services
- Initialize the database with test data (if empty)
- Create tables and populate stores, menus, and users

### 2. Access the Application

Once the containers are running:

- **Frontend**: Open your browser and go to http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

## Database Initialization

The application automatically initializes the database on first run with:

**Test Stores:**
- Grill Chef Main
- Grill Chef Downtown

**Menu Items:** (8 items per store)
- Grilled Chicken Souvlaki
- Lamb Kofta
- Grilled Fish
- Greek Salad
- Appetizers (Hummus, Tzatziki, Falafel)
- And more...

**Test Users:**
- john@example.com - John Doe
- jane@example.com - Jane Smith
- test@example.com - Test User

The database is stored in a Docker volume (`backend_db`) so data persists between container restarts.

## Common Docker Commands

### Start the Application
```bash
docker-compose up
```

### Start in Background
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop the Application
```bash
docker-compose down
```

### Stop and Remove All Data
```bash
docker-compose down -v
```

### Rebuild Images
```bash
docker-compose up --build
```

### Restart Services
```bash
docker-compose restart
```

## Development Workflow

### With Auto-Reload
The containers are configured with volume mounts, so code changes automatically reload:
- Backend: uvicorn auto-reload is enabled
- Frontend: Changes are visible on browser refresh

### Accessing Container Shell
```bash
# Backend shell
docker exec -it grill-chef-backend bash

# Frontend shell
docker exec -it grill-chef-frontend bash
```

### Run Commands in Containers
```bash
# Run Python script in backend
docker exec grill-chef-backend python script.py

# Run Node command in frontend
docker exec grill-chef-frontend node command.js
```

## Database File Location

The SQLite database file is stored in a Docker volume. To access it:

```bash
# The database file is in: /app/data/food_order.db inside the backend container
docker exec grill-chef-backend ls -la /app/data/
```

## Resetting the Database

To clear all data and reinitialize:

```bash
# Option 1: Remove volume and restart
docker-compose down -v
docker-compose up

# Option 2: Delete database file only
docker exec grill-chef-backend rm /app/data/food_order.db
docker-compose restart backend
```

## Troubleshooting

### Port Already in Use
If port 3000 or 8000 is already in use:

```bash
# Modify docker-compose.yml to use different ports:
# Change "3000:3000" to "3001:3000"
# Change "8000:8000" to "8001:8000"
```

### Backend Connection Errors
If frontend can't connect to backend:
1. Ensure both containers are running: `docker-compose ps`
2. Check backend logs: `docker-compose logs backend`
3. Verify network connectivity: `docker-compose logs`

### Database Not Initializing
```bash
# Check if init_db.py ran successfully
docker-compose logs backend | grep "init_db\|Database\|✓"

# Reinitialize database
docker exec grill-chef-backend python init_db.py
```

### Build Failures
```bash
# Clean rebuild
docker-compose down
docker system prune -a
docker-compose up --build
```

## Environment Variables

Backend environment variables (in docker-compose.yml):
- `DATABASE_URL`: SQLite database path (default: `sqlite:////app/data/food_order.db`)
- `PYTHONUNBUFFERED`: Set to 1 for real-time log output

Frontend detects Docker based on hostname and automatically configures the API endpoint.

## Monitoring

### Container Status
```bash
docker-compose ps
```

### Resource Usage
```bash
docker stats
```

### Health Checks
The backend includes health checks that verify the API is responding:
```bash
docker-compose ps  # Shows health status
```

## Performance Notes

- First startup may take 30-60 seconds as Docker builds images
- Database initialization happens automatically (only on first run with empty DB)
- Subsequent startups are faster

## Next Steps

1. Navigate to http://localhost:3000 to use the app
2. Check backend docs at http://localhost:8000/docs
3. Test the API endpoints
4. Modify code in your editor - changes reload automatically

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Verify Docker is running
- Ensure ports 3000 and 8000 are available
- Review the troubleshooting section above
