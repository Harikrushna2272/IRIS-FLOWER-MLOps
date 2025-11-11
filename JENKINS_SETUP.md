# Jenkins CI/CD Setup Guide

This guide will help you set up and configure Jenkins for your MLOps project with automated CI/CD pipelines.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Manual Setup](#manual-setup)
- [Jenkins Configuration](#jenkins-configuration)
- [Creating Your First Pipeline](#creating-your-first-pipeline)
- [Pipeline Stages Explained](#pipeline-stages-explained)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:
- Docker (version 20.10 or higher)
- Docker Compose (version 1.29 or higher)
- Git

## Quick Start

The easiest way to set up Jenkins is using our setup script:

```bash
# Make the script executable (if not already)
chmod +x jenkins-setup.sh

# Run the setup script
./jenkins-setup.sh
```

This script will:
1. Check for Docker and Docker Compose
2. Start Jenkins in a Docker container
3. Display the initial admin password
4. Provide next steps

## Manual Setup

If you prefer to set up Jenkins manually:

### 1. Start Jenkins Container

```bash
docker-compose -f docker-compose.jenkins.yml up -d
```

### 2. Get Initial Admin Password

Wait about 30 seconds for Jenkins to initialize, then run:

```bash
docker exec jenkins_server cat /var/jenkins_home/secrets/initialAdminPassword
```

Copy this password - you'll need it for the initial setup.

### 3. Access Jenkins

Open your browser and navigate to:
```
http://localhost:8080
```

## Jenkins Configuration

### Initial Setup

1. **Unlock Jenkins**: Paste the initial admin password you copied earlier

2. **Install Plugins**: Click "Install suggested plugins"
   - Wait for the installation to complete (this may take a few minutes)

3. **Create Admin User**: Fill in the form to create your admin user:
   - Username: (your choice)
   - Password: (your choice)
   - Full name: (your choice)
   - Email: (your email)

4. **Instance Configuration**: Keep the default Jenkins URL and click "Save and Finish"

### Install Required Plugins

After the initial setup, install these additional plugins:

1. Go to **Manage Jenkins** → **Manage Plugins**
2. Click on the **Available** tab
3. Search and select:
   - `Docker Pipeline` (if not already installed)
   - `Docker` (if not already installed)
   - `Git` (usually pre-installed)
4. Click **Install without restart**

### Configure Docker Access

Jenkins needs access to Docker to build and run containers:

1. Go to **Manage Jenkins** → **Manage Nodes and Clouds**
2. Click on **Configure Clouds**
3. Add a new Docker cloud if needed
4. Test the connection

**Note**: Our `docker-compose.jenkins.yml` already mounts the Docker socket, so Docker should work out of the box.

## Creating Your First Pipeline

### Option 1: Using SCM (Git) - Recommended

1. **Create New Item**:
   - Click **New Item** from the Jenkins dashboard
   - Enter a name (e.g., "MLOps-Pipeline")
   - Select **Pipeline**
   - Click **OK**

2. **Configure Pipeline**:
   - Scroll to the **Pipeline** section
   - Select **Pipeline script from SCM**
   - Choose **Git** as SCM
   - Enter your repository URL
   - Specify the branch (e.g., `main` or `master`)
   - Set **Script Path** to `Jenkinsfile`
   - Click **Save**

3. **Run Pipeline**:
   - Click **Build Now**
   - Watch the pipeline execute in real-time

### Option 2: Direct Pipeline Script

1. **Create New Item**: Same as above
2. **Configure Pipeline**:
   - In the Pipeline section, select **Pipeline script**
   - Copy and paste the contents of your `Jenkinsfile`
   - Click **Save**
3. **Run Pipeline**: Click **Build Now**

## Pipeline Stages Explained

Our Jenkinsfile includes the following stages:

### 1. **Checkout**
```groovy
stage('Checkout') { ... }
```
- Pulls the latest code from your Git repository
- Ensures you're building the most recent version

### 2. **Environment Setup**
```groovy
stage('Environment Setup') { ... }
```
- Verifies Python, Docker, and Docker Compose are available
- Displays version information for debugging

### 3. **Build Docker Images**
```groovy
stage('Build Docker Images') { ... }
```
- Builds both API and DB service Docker images
- Uses `--no-cache` to ensure fresh builds

### 4. **Run Tests**
```groovy
stage('Run Tests') { ... }
```
- Runs pytest tests for both services
- Tests are run in isolated Docker containers
- Pipeline fails if any tests fail

### 5. **Stop Existing Containers**
```groovy
stage('Stop Existing Containers') { ... }
```
- Stops and removes old containers
- Prepares for fresh deployment

### 6. **Deploy**
```groovy
stage('Deploy') { ... }
```
- Starts services using docker-compose
- Runs containers in detached mode

### 7. **Health Check**
```groovy
stage('Health Check') { ... }
```
- Verifies both services are responding
- Checks endpoints at localhost:8000 and localhost:8001
- Fails if services don't respond

### 8. **Cleanup Old Images**
```groovy
stage('Cleanup Old Images') { ... }
```
- Removes unused Docker images
- Keeps your system clean

## Testing Your Services

The project includes test files for both services:

### API Service Tests (`api/test_main.py`)
- Tests home endpoint
- Tests prediction endpoint
- Tests model integration
- Tests error handling

### DB Service Tests (`db/test_main.py`)
- Tests CRUD operations
- Tests database connections
- Tests data validation

### Running Tests Locally

Before pushing to Jenkins, you can run tests locally:

```bash
# Test API service
cd api
uv run pytest test_main.py -v

# Test DB service
cd ../db
uv run pytest test_main.py -v
```

## Webhook Configuration (Optional)

To automatically trigger builds when you push to Git:

### GitHub Webhook

1. Go to your GitHub repository → **Settings** → **Webhooks**
2. Click **Add webhook**
3. Set Payload URL to: `http://your-server:8080/github-webhook/`
4. Select **application/json** as content type
5. Choose "Just the push event"
6. Click **Add webhook**

### Jenkins Configuration

1. Go to your pipeline job → **Configure**
2. Under **Build Triggers**, check:
   - `GitHub hook trigger for GITScm polling`
3. Click **Save**

**Note**: For local development, you may need tools like ngrok to expose your Jenkins instance to GitHub.

## Environment Variables

The pipeline uses these environment variables:

- `DOCKER_COMPOSE_FILE`: Path to docker-compose.yml (default: `docker-compose.yml`)
- `PROJECT_NAME`: Project identifier (default: `trial-mlops`)

You can modify these in the `environment` section of the Jenkinsfile.

## Monitoring Pipeline Execution

### Console Output
- Click on a build number → **Console Output**
- Shows real-time logs of the pipeline execution

### Blue Ocean (Optional)
- Install the Blue Ocean plugin for a modern UI
- Go to **Open Blue Ocean** from the Jenkins menu
- Visualizes pipeline stages and status

## Stopping Jenkins

To stop the Jenkins server:

```bash
docker-compose -f docker-compose.jenkins.yml down
```

To stop and remove all data (including configuration):

```bash
docker-compose -f docker-compose.jenkins.yml down -v
```

## Troubleshooting

### Issue: "Cannot connect to Docker daemon"

**Solution**: Ensure Docker is running and the socket is properly mounted:
```bash
docker ps  # Should list running containers
```

### Issue: Tests failing in Jenkins but passing locally

**Solution**:
- Check that all dependencies are in `pyproject.toml`
- Verify environment variables are set correctly
- Check Docker container logs

### Issue: Port conflicts (8080, 8000, 8001)

**Solution**:
- Stop conflicting services
- Or modify ports in `docker-compose.jenkins.yml` and `docker-compose.yml`

### Issue: Jenkins is slow or unresponsive

**Solution**:
- Increase Docker resources (CPU/Memory)
- Check disk space: `docker system df`
- Clean up: `docker system prune -a`

### Issue: Pipeline fails at Health Check stage

**Solution**:
- Increase sleep time in Health Check stage
- Check if services are starting correctly: `docker-compose logs`
- Verify ports are not in use: `lsof -i :8000` and `lsof -i :8001`

### Viewing Jenkins Logs

```bash
# View real-time logs
docker logs -f jenkins_server

# View last 100 lines
docker logs --tail 100 jenkins_server
```

### Accessing Jenkins Container

If you need to debug inside the Jenkins container:

```bash
docker exec -it jenkins_server bash
```

## Best Practices

1. **Version Control**: Always commit your Jenkinsfile to version control
2. **Test Locally**: Run tests locally before pushing
3. **Use Branches**: Create feature branches and test pipelines before merging to main
4. **Monitor Resources**: Keep an eye on Docker disk usage
5. **Backup Jenkins**: Regularly backup `/var/jenkins_home` volume
6. **Security**: Change default passwords and enable authentication
7. **Clean Up**: Regularly remove old Docker images and containers

## Pipeline Customization

You can customize the pipeline by modifying `Jenkinsfile`:

### Add Email Notifications

```groovy
post {
    success {
        mail to: 'team@example.com',
             subject: "Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
             body: "Build succeeded!"
    }
    failure {
        mail to: 'team@example.com',
             subject: "Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
             body: "Build failed. Check console output."
    }
}
```

### Add Slack Notifications

```groovy
post {
    success {
        slackSend color: 'good', message: "Build succeeded: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
    }
    failure {
        slackSend color: 'danger', message: "Build failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
    }
}
```

### Add Code Quality Checks

```groovy
stage('Code Quality') {
    steps {
        sh '''
            cd api
            uv run pylint main.py || true
            uv run black --check main.py || true
        '''
    }
}
```

## Next Steps

After successful setup:

1. **Set up automated triggers**: Configure webhooks for automatic builds
2. **Add more tests**: Expand test coverage for your services
3. **Implement staging**: Add a staging environment before production
4. **Add monitoring**: Integrate monitoring tools like Prometheus/Grafana
5. **Security scanning**: Add container security scanning to your pipeline
6. **Documentation**: Document your specific deployment procedures

## Additional Resources

- [Jenkins Official Documentation](https://www.jenkins.io/doc/)
- [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-workflow/)
- [Jenkins Best Practices](https://www.jenkins.io/doc/book/pipeline/pipeline-best-practices/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Support

If you encounter issues:
1. Check Jenkins console output for detailed error messages
2. Review Docker logs: `docker-compose logs`
3. Check system resources: `docker stats`
4. Verify all prerequisites are installed correctly

---

**Happy CI/CD! 🚀**
