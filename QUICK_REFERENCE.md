# Quick Reference Guide

## Essential Commands

### Starting Services

```bash
# Start main application
docker-compose up -d

# Start Jenkins
./jenkins-setup.sh
# OR
docker-compose -f docker-compose.jenkins.yml up -d

# Start everything in background
docker-compose up -d && docker-compose -f docker-compose.jenkins.yml up -d
```

### Stopping Services

```bash
# Stop main application
docker-compose down

# Stop Jenkins
docker-compose -f docker-compose.jenkins.yml down

# Stop and remove volumes
docker-compose down -v
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f db

# Jenkins logs
docker logs -f jenkins_server
```

### Running Tests

```bash
# API tests
cd api && uv run pytest test_main.py -v

# DB tests
cd db && uv run pytest test_main.py -v
```

### Docker Cleanup

```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -a -f

# Remove unused volumes
docker volume prune -f

# Complete cleanup (WARNING: removes everything)
docker system prune -a -f --volumes
```

## URLs

| Service | URL | Purpose |
|---------|-----|---------|
| API Service | http://localhost:8000 | Main prediction interface |
| DB Service | http://localhost:8001 | Database API |
| Jenkins | http://localhost:8080 | CI/CD dashboard |

## Jenkins Initial Password

```bash
docker exec jenkins_server cat /var/jenkins_home/secrets/initialAdminPassword
```

## Common Issues & Fixes

### Port Already in Use

```bash
# Find process using port
lsof -i :8000
lsof -i :8080

# Kill process
kill -9 <PID>
```

### Container Won't Start

```bash
# Check logs
docker-compose logs <service-name>

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Tests Failing

```bash
# Check if dependencies are installed
cd api && uv pip list
cd db && uv pip list

# Reinstall dependencies
cd api && uv sync
cd db && uv sync
```

### Jenkins Pipeline Fails

```bash
# Check Jenkins logs
docker logs jenkins_server

# Restart Jenkins
docker-compose -f docker-compose.jenkins.yml restart

# Check if Docker socket is accessible
docker exec jenkins_server docker ps
```

## File Structure

```
TRIAL_MLOps/
├── api/
│   ├── main.py              # API logic
│   ├── test_main.py         # Tests
│   ├── model.pkl            # ML model
│   ├── Dockerfile
│   └── pyproject.toml
├── db/
│   ├── main.py              # DB logic
│   ├── test_main.py         # Tests
│   ├── Dockerfile
│   └── pyproject.toml
├── docker-compose.yml       # Main services
├── docker-compose.jenkins.yml  # Jenkins
├── Jenkinsfile              # CI/CD pipeline
├── jenkins-setup.sh         # Setup script
├── JENKINS_SETUP.md         # Full documentation
└── README.md                # Overview
```

## Jenkins Pipeline Stages

1. **Checkout** - Get code from Git
2. **Environment Setup** - Verify prerequisites
3. **Build** - Create Docker images
4. **Test** - Run unit tests
5. **Stop Old Containers** - Clean up
6. **Deploy** - Start new containers
7. **Health Check** - Verify deployment
8. **Cleanup** - Remove old images

## Environment Variables

### API Service (.env)
```bash
DATABASE_SERVICE_URL=http://db:8001
```

### Jenkins (in Jenkinsfile)
```groovy
DOCKER_COMPOSE_FILE=docker-compose.yml
PROJECT_NAME=trial-mlops
```

## Useful Docker Commands

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# View container stats
docker stats

# Execute command in container
docker exec -it <container_name> bash

# Copy file from container
docker cp <container_name>:/path/to/file ./local/path

# View container resource usage
docker stats --no-stream
```

## API Endpoints Quick Reference

### API Service (Port 8000)
- `GET /` - Main UI
- `POST /predict` - Make prediction
- `GET /show-result` - View history

### DB Service (Port 8001)
- `GET /` - Health check
- `POST /prediction` - Save prediction
- `GET /prediction` - Get all predictions

## Testing Endpoints with curl

```bash
# Test API health
curl http://localhost:8000/

# Test DB health
curl http://localhost:8001/health

# Create prediction (DB service)
curl -X POST http://localhost:8001/prediction \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2,
    "predicted_class": "Setosa"
  }'

# Get all predictions
curl http://localhost:8001/prediction
```

## Jenkins Job Configuration

### Create Pipeline Job
1. New Item → Enter name → Pipeline → OK
2. Pipeline section:
   - **Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: (your repo)
   - **Branch**: main
   - **Script Path**: Jenkinsfile
3. Save

### Trigger Build
- Manual: Click "Build Now"
- Automatic: Set up webhook (see JENKINS_SETUP.md)

## Backup & Restore

### Backup Jenkins
```bash
# Backup Jenkins home
docker run --rm -v jenkins_home:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/jenkins_backup.tar.gz /data
```

### Backup Database
```bash
# Backup SQLite database
docker cp db_service:/app/data/db.sqlite3 ./backup/
```

### Restore
```bash
# Restore Jenkins
docker run --rm -v jenkins_home:/data -v $(pwd):/backup \
  ubuntu bash -c "cd /data && tar xzf /backup/jenkins_backup.tar.gz --strip 1"

# Restore Database
docker cp ./backup/db.sqlite3 db_service:/app/data/
```

## Performance Tuning

### Increase Docker Resources
Edit Docker Desktop → Resources:
- CPUs: 4+
- Memory: 4GB+
- Swap: 1GB+
- Disk: 60GB+

### Jenkins Optimization
- Manage Jenkins → System Configuration
- Set # of executors to match CPU cores
- Increase Java heap size if needed

## Security Checklist

- [ ] Change Jenkins admin password
- [ ] Enable CSRF protection
- [ ] Configure user authentication
- [ ] Use secrets for sensitive data
- [ ] Keep Docker images updated
- [ ] Regular backup of data
- [ ] Monitor container logs
- [ ] Use .env for environment variables

## Monitoring

```bash
# Real-time resource usage
docker stats

# Disk usage
docker system df

# Container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Network connectivity
docker network inspect trial-mlops_default
```

## Getting Help

1. Check logs: `docker-compose logs -f`
2. Review [JENKINS_SETUP.md](JENKINS_SETUP.md)
3. Check [README.md](README.md)
4. Examine Jenkins console output
5. Verify Docker is running: `docker ps`

---

**Keep this guide handy for quick reference!**
