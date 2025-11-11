# GitHub + Jenkins Integration Guide

This guide explains how to integrate your GitHub repository with Jenkins for automated CI/CD.

## Repository Information

- **GitHub Repository**: https://github.com/Harikrushna2272/IRIS-FLOWER-MLOps.git
- **Branch**: main

## Table of Contents
- [Quick Setup](#quick-setup)
- [Jenkins Pipeline Configuration](#jenkins-pipeline-configuration)
- [Webhook Setup](#webhook-setup-automated-builds)
- [Troubleshooting](#troubleshooting)

## Quick Setup

### 1. Start Jenkins

```bash
cd /Users/apple/Documents/Technology/Practical_world/TRIAL_MLOps
./jenkins-setup.sh
```

Access Jenkins at: **http://localhost:8080**

### 2. Complete Initial Setup

1. Unlock Jenkins with the initial admin password
2. Install suggested plugins
3. Create admin user
4. Install additional plugins:
   - Git plugin (usually pre-installed)
   - GitHub plugin
   - Docker Pipeline

## Jenkins Pipeline Configuration

### Create New Pipeline Job

**Step 1: Create Item**
- Click "New Item" in Jenkins dashboard
- Enter name: `IRIS-MLOps-Pipeline`
- Select "Pipeline"
- Click "OK"

**Step 2: General Configuration**
- Description: `CI/CD pipeline for IRIS Flower MLOps project`
- ✓ Check "GitHub project"
- Project URL: `https://github.com/Harikrushna2272/IRIS-FLOWER-MLOps/`

**Step 3: Pipeline Configuration**
- Pipeline Definition: `Pipeline script from SCM`
- SCM: `Git`
- Repository URL: `https://github.com/Harikrushna2272/IRIS-FLOWER-MLOps.git`
- Credentials: (leave blank for public repo)
- Branch Specifier: `*/main`
- Script Path: `Jenkinsfile`

**Step 4: Save and Build**
- Click "Save"
- Click "Build Now"

## Webhook Setup (Automated Builds)

Enable automatic builds when you push to GitHub.

### For Local Jenkins (Using ngrok)

Since Jenkins is running locally, expose it to the internet:

**1. Install ngrok:**
```bash
brew install ngrok
```

**2. Create ngrok account** (free): https://ngrok.com/

**3. Configure ngrok:**
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

**4. Expose Jenkins:**
```bash
ngrok http 8080
```
Copy the forwarding URL (e.g., `https://abc123.ngrok.io`)

**5. Configure GitHub Webhook:**
- Go to repository: https://github.com/Harikrushna2272/IRIS-FLOWER-MLOps/settings/hooks
- Click "Add webhook"
- Payload URL: `https://abc123.ngrok.io/github-webhook/`
- Content type: `application/json`
- Events: "Just the push event"
- ✓ Active
- Click "Add webhook"

**6. Configure Jenkins Job:**
- Pipeline → Configure
- Build Triggers → ✓ "GitHub hook trigger for GITScm polling"
- Save

### Testing the Webhook

```bash
echo "# Test webhook" >> README.md
git add README.md
git commit -m "Test webhook trigger"
git push origin main
```

Check Jenkins - a build should start automatically!

## Manual Trigger (Without Webhook)

### Option 1: Poll SCM
- Jenkins job → Configure → Build Triggers
- ✓ "Poll SCM"
- Schedule: `H/5 * * * *` (checks every 5 minutes)

### Option 2: Manual Build
- Click "Build Now" whenever you push changes

## Using Private Repository

If your repository is private:

**1. Create GitHub Personal Access Token:**
- GitHub → Settings → Developer settings → Personal access tokens
- Generate new token (classic)
- Scopes: Select `repo`
- Copy the token

**2. Add Credentials in Jenkins:**
- Jenkins → Manage Jenkins → Credentials
- Click "(global)" domain
- "Add Credentials"
- Kind: `Username with password`
- Username: Your GitHub username
- Password: Paste the token
- ID: `github-credentials`
- Click "Create"

**3. Use in Pipeline:**
- Pipeline configuration → Credentials → Select your credential

## Common Commands

### Git Commands
```bash
# Check status
git status

# Pull latest
git pull origin main

# Commit and push
git add .
git commit -m "Your message"
git push origin main
```

### Jenkins Commands
```bash
# Start Jenkins
./jenkins-setup.sh

# Stop Jenkins
docker-compose -f docker-compose.jenkins.yml down

# View logs
docker logs -f jenkins_server
```

## Pull Request Workflow

**1. Create Feature Branch:**
```bash
git checkout -b feature/new-feature
```

**2. Make Changes and Commit:**
```bash
git add .
git commit -m "Add new feature"
```

**3. Push Branch:**
```bash
git push origin feature/new-feature
```

**4. Create Pull Request:**
- Go to GitHub repository
- Click "Compare & pull request"
- Jenkins will test the PR
- Merge after tests pass

## Troubleshooting

### Jenkins Can't Access GitHub
- Verify repository URL
- Check if private (add credentials)
- Ensure Git plugin installed

### Webhook Not Triggering
- Verify webhook URL is correct
- Check "GitHub hook trigger" is enabled
- For local Jenkins, ensure ngrok is running
- Check GitHub webhook delivery logs

### Build Fails
- Check Jenkins console output
- Verify Docker is available
- Check environment variables

### Permission Denied for Docker
```bash
docker exec -u root jenkins_server usermod -aG docker jenkins
docker-compose -f docker-compose.jenkins.yml restart
```

## Best Practices

1. Small, frequent commits
2. Use feature branches
3. Code reviews via pull requests
4. Test before push
5. Keep main branch stable
6. Use semantic commit messages:
   - `feat:` for features
   - `fix:` for bug fixes
   - `docs:` for documentation

## Resources

- **Repository**: https://github.com/Harikrushna2272/IRIS-FLOWER-MLOps
- **Jenkins**: http://localhost:8080
- **GitHub Webhooks**: https://docs.github.com/en/webhooks
- **ngrok**: https://ngrok.com/docs

---

**Happy Continuous Integration! 🚀**
