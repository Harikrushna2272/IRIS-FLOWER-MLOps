# MLOps Project - Iris Prediction with CI/CD

A complete MLOps project demonstrating microservices architecture, Docker containerization, and Jenkins CI/CD pipeline.

## Project Overview

This project implements a machine learning application for Iris flower classification using:
- **FastAPI** for REST API services
- **Docker & Docker Compose** for containerization
- **Jenkins** for CI/CD automation
- **Microservices architecture** with separate API and Database services

## Architecture

```
┌─────────────────┐
│   API Service   │  (Port 8000)
│   - FastAPI     │
│   - ML Model    │
│   - Web UI      │
└────────┬────────┘
         │
         ↓ HTTP
┌────────┴────────┐
│   DB Service    │  (Port 8001)
│   - FastAPI     │
│   - SQLite      │
│   - Tortoise ORM│
└─────────────────┘
```

## Services

### API Service (Port 8000)
- Serves web interface for predictions
- Loads pre-trained Iris classification model
- Makes predictions based on user input
- Sends predictions to DB service for storage
- Displays historical predictions

### DB Service (Port 8001)
- Stores prediction records
- Provides REST API for CRUD operations
- Uses SQLite database with Tortoise ORM

## Quick Start

### Running the Application

```bash
# Start both services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application at:
- API Service: http://localhost:8000
- DB Service: http://localhost:8001

### Running with Jenkins CI/CD

```bash
# Start Jenkins server
./jenkins-setup.sh

# Or manually
docker-compose -f docker-compose.jenkins.yml up -d
```

See [JENKINS_SETUP.md](JENKINS_SETUP.md) for complete CI/CD setup instructions.

## Development

### Project Structure

```
TRIAL_MLOps/
├── api/                    # API service
│   ├── main.py            # FastAPI application
│   ├── model.pkl          # Pre-trained ML model
│   ├── test_main.py       # Unit tests
│   ├── templates/         # HTML templates
│   ├── Dockerfile         # API container config
│   └── pyproject.toml     # Dependencies
│
├── db/                     # Database service
│   ├── main.py            # FastAPI DB service
│   ├── test_main.py       # Unit tests
│   ├── data/              # SQLite database
│   ├── Dockerfile         # DB container config
│   └── pyproject.toml     # Dependencies
│
├── docker-compose.yml      # Main services
├── docker-compose.jenkins.yml  # Jenkins setup
├── Jenkinsfile            # CI/CD pipeline
├── jenkins-setup.sh       # Setup script
├── JENKINS_SETUP.md       # CI/CD documentation
└── README.md              # This file
```

### Running Tests

```bash
# Test API service
cd api
uv run pytest test_main.py -v

# Test DB service
cd db
uv run pytest test_main.py -v
```

### Adding Dependencies

Update the respective `pyproject.toml` file:

```bash
# For API service
cd api
uv add package-name

# For DB service
cd db
uv add package-name
```

## CI/CD Pipeline

The Jenkins pipeline includes these stages:

1. **Checkout** - Pull latest code from Git
2. **Environment Setup** - Verify tools are available
3. **Build Docker Images** - Build API and DB containers
4. **Run Tests** - Execute unit tests
5. **Stop Existing Containers** - Clean up old deployments
6. **Deploy** - Start new containers
7. **Health Check** - Verify services are running
8. **Cleanup** - Remove unused Docker images

### Pipeline Triggers

- Manual: Click "Build Now" in Jenkins
- Automatic: Push to Git repository (requires webhook setup)

## API Endpoints

### API Service (http://localhost:8000)

- `GET /` - Web interface for predictions
- `POST /predict` - Submit prediction request
- `GET /show-result` - View prediction history

### DB Service (http://localhost:8001)

- `GET /` - Health check
- `GET /health` - Service status
- `POST /prediction` - Create prediction record
- `GET /prediction` - Get all predictions

## Environment Variables

### API Service
- `DATABASE_SERVICE_URL` - URL of DB service (default: http://db:8001)

### Jenkins
- `DOCKER_COMPOSE_FILE` - Compose file to use (default: docker-compose.yml)
- `PROJECT_NAME` - Project identifier (default: trial-mlops)

## Technologies Used

- **Python 3.11** - Programming language
- **FastAPI** - Web framework
- **scikit-learn** - ML library
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Jenkins** - CI/CD automation
- **Tortoise ORM** - Database ORM
- **SQLite** - Database
- **Pytest** - Testing framework
- **UV** - Python package manager

## Monitoring & Debugging

### View Container Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f db
```

### Check Container Status

```bash
docker-compose ps
```

### Execute Commands in Container

```bash
# API service
docker exec -it api_service bash

# DB service
docker exec -it db_service bash
```

### View Database

```bash
# Access SQLite database
docker exec -it db_service sqlite3 /app/data/db.sqlite3
```

## Troubleshooting

### Port Already in Use

```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change ports in docker-compose.yml
```

### Docker Issues

```bash
# Clean up Docker system
docker system prune -a

# Remove all stopped containers
docker container prune

# Remove unused volumes
docker volume prune
```

### Jenkins Not Starting

```bash
# View Jenkins logs
docker logs -f jenkins_server

# Restart Jenkins
docker-compose -f docker-compose.jenkins.yml restart
```

## Best Practices

1. Always run tests before pushing to production
2. Use feature branches for development
3. Review Jenkins pipeline logs for issues
4. Keep Docker images clean with regular pruning
5. Monitor resource usage with `docker stats`
6. Backup database regularly
7. Use environment variables for configuration

## Future Enhancements

- [ ] Add model versioning
- [ ] Implement model retraining pipeline
- [ ] Add monitoring with Prometheus/Grafana
- [ ] Implement authentication/authorization
- [ ] Add API rate limiting
- [ ] Deploy to cloud (AWS/GCP/Azure)
- [ ] Add integration tests
- [ ] Implement blue-green deployment
- [ ] Add performance testing
- [ ] Set up log aggregation

## Documentation

- [Jenkins Setup Guide](JENKINS_SETUP.md) - Complete CI/CD setup instructions
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is for educational purposes.

## Support

For issues and questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Jenkins console output
3. Check Docker logs
4. Refer to [JENKINS_SETUP.md](JENKINS_SETUP.md)

---

**Built with ❤️ for learning MLOps**
