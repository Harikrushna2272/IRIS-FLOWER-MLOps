#!/bin/bash

# Jenkins Setup Script for MLOps Project
# This script helps you set up Jenkins with Docker support

echo "=========================================="
echo "Jenkins CI/CD Setup for MLOps Project"
echo "=========================================="

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if Docker is installed
echo ""
echo "Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is installed"

# Start Jenkins
echo ""
echo "Starting Jenkins server..."
docker-compose -f docker-compose.jenkins.yml up -d

if [ $? -eq 0 ]; then
    print_success "Jenkins server started successfully"
else
    print_error "Failed to start Jenkins server"
    exit 1
fi

# Wait for Jenkins to start
echo ""
echo "Waiting for Jenkins to initialize (this may take a minute)..."
sleep 30

# Get initial admin password
echo ""
echo "=========================================="
echo "Jenkins Initial Setup Information"
echo "=========================================="
echo ""
echo "Jenkins URL: http://localhost:8080"
echo ""

if docker exec jenkins_server test -f /var/jenkins_home/secrets/initialAdminPassword; then
    ADMIN_PASSWORD=$(docker exec jenkins_server cat /var/jenkins_home/secrets/initialAdminPassword)
    print_success "Initial Admin Password: $ADMIN_PASSWORD"
    echo ""
    echo "Copy this password, you'll need it for the initial setup!"
else
    print_warning "Could not retrieve admin password. Please wait a bit longer and run:"
    echo "docker exec jenkins_server cat /var/jenkins_home/secrets/initialAdminPassword"
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Open http://localhost:8080 in your browser"
echo "2. Enter the initial admin password shown above"
echo "3. Install suggested plugins"
echo "4. Create your first admin user"
echo "5. Install 'Docker Pipeline' plugin from Manage Jenkins > Plugins"
echo "6. Create a new Pipeline job and point it to your Jenkinsfile"
echo ""
echo "To stop Jenkins: docker-compose -f docker-compose.jenkins.yml down"
echo "To view logs: docker logs -f jenkins_server"
echo ""
print_success "Setup complete!"
