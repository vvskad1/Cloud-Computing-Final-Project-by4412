# AWS Deployment Guide - FixIt Tech Solutions

**CS 623 Final Project - Cloud Deployment**

---

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [AWS Services Used](#aws-services-used)
3. [Prerequisites](#prerequisites)
4. [Deployment Options](#deployment-options)
5. [Option 1: EC2 Deployment (Recommended for Learning)](#option-1-ec2-deployment-recommended)
6. [Option 2: Elastic Beanstalk Deployment](#option-2-elastic-beanstalk-deployment)
7. [Option 3: Docker + ECS Deployment](#option-3-docker--ecs-deployment)
8. [Database Configuration](#database-configuration)
9. [Security Configuration](#security-configuration)
10. [Domain and SSL Setup](#domain-and-ssl-setup)
11. [Monitoring and Logging](#monitoring-and-logging)
12. [Cost Estimation](#cost-estimation)
13. [Troubleshooting](#troubleshooting)

---

## Deployment Overview

This guide covers deploying FixIt Tech Solutions to AWS using three different approaches:

- **EC2**: Manual deployment on virtual server (best for learning)
- **Elastic Beanstalk**: Platform-as-a-Service with automatic scaling
- **ECS with Docker**: Containerized deployment for production

All methods use AWS Free Tier eligible services where possible.

---

## AWS Services Used

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| **EC2** | Virtual server for application | 750 hours/month (t2.micro) |
| **RDS** | Managed PostgreSQL database | 750 hours/month (db.t2.micro) |
| **S3** | Static file storage (optional) | 5GB storage |
| **Route 53** | DNS management | $0.50/hosted zone/month |
| **CloudWatch** | Logging and monitoring | 10 custom metrics |
| **Security Groups** | Firewall rules | Free |
| **Elastic IP** | Static IP address | Free when attached |
| **IAM** | Access management | Free |

---

## Prerequisites

### Local Requirements

- AWS Account (with Free Tier if possible)
- AWS CLI installed
- SSH client (PuTTY for Windows or native SSH)
- Project files from this repository

### AWS Account Setup

1. **Create AWS Account**: https://aws.amazon.com/free/
2. **Enable MFA** (Multi-Factor Authentication) for security
3. **Create IAM User** (don't use root account):
   - Go to IAM Console
   - Create user with Administrator Access
   - Save Access Key ID and Secret Access Key

### Install AWS CLI

**Windows:**
```powershell
# Download and install from: https://aws.amazon.com/cli/
# Or use MSI installer
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

**macOS:**
```bash
brew install awscli
```

**Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**Configure AWS CLI:**
```bash
aws configure
# Enter: Access Key ID, Secret Access Key, Default region (us-east-1), Output format (json)
```

---

## Deployment Options

### Comparison Matrix

| Feature | EC2 | Elastic Beanstalk | ECS (Docker) |
|---------|-----|-------------------|--------------|
| **Complexity** | Medium | Low | High |
| **Control** | Full | Medium | Full |
| **Setup Time** | 30-45 min | 15-20 min | 45-60 min |
| **Scaling** | Manual | Automatic | Automatic |
| **Cost** | Low | Medium | Medium-High |
| **Best For** | Learning, Testing | Quick Deploy | Production |
| **Free Tier** | ✅ Yes | ✅ Yes | ✅ Limited |

---

## Option 1: EC2 Deployment (Recommended)

### Step 1: Launch EC2 Instance

1. **Go to EC2 Console**: https://console.aws.amazon.com/ec2/

2. **Click "Launch Instance"**

3. **Configure Instance:**
   - **Name**: fixit-tech-server
   - **AMI**: Ubuntu Server 22.04 LTS (Free Tier)
   - **Instance Type**: t2.micro (1 vCPU, 1GB RAM - Free Tier)
   - **Key Pair**: Create new key pair
     - Name: fixit-tech-key
     - Type: RSA
     - Format: .pem (Mac/Linux) or .ppk (Windows/PuTTY)
     - **Download and save securely!**

4. **Network Settings:**
   - Create security group: fixit-tech-sg
   - Allow SSH (port 22) from your IP
   - Allow HTTP (port 80) from anywhere (0.0.0.0/0)
   - Allow HTTPS (port 443) from anywhere (0.0.0.0/0)
   - Allow Custom TCP (port 8081) from anywhere (for testing)

5. **Storage:** 8GB gp3 (Free Tier)

6. **Click "Launch Instance"**

7. **Wait for instance to be "Running"** (2-3 minutes)

### Step 2: Connect to EC2 Instance

**Get Public IP:**
- Select your instance in EC2 console
- Copy "Public IPv4 address" (e.g., 3.15.123.45)

**Windows (using PuTTY):**
```powershell
# Convert .pem to .ppk using PuTTYgen
# Then connect via PuTTY:
# Host: ubuntu@<public-ip>
# Auth: Browse to .ppk file
```

**Mac/Linux:**
```bash
# Set key permissions
chmod 400 fixit-tech-key.pem

# Connect via SSH
ssh -i fixit-tech-key.pem ubuntu@<public-ip>
```

### Step 3: Setup Server Environment

Once connected to EC2:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Nginx (web server)
sudo apt install nginx -y

# Install Git
sudo apt install git -y

# Verify installations
python3.11 --version
nginx -v
```

### Step 4: Upload Application Files

**Option A: Using SCP (from your local machine):**

```bash
# Navigate to your project folder locally
cd "C:\Users\STSC\Desktop\Cloud Computing Final Project"

# Copy entire project to EC2
scp -i fixit-tech-key.pem -r . ubuntu@<public-ip>:/home/ubuntu/fixit-tech/
```

**Option B: Using Git (if you have a repository):**

```bash
# On EC2 instance
cd /home/ubuntu
git clone <your-repo-url> fixit-tech
cd fixit-tech
```

**Option C: Manual upload via SFTP:**
- Use FileZilla or WinSCP
- Connect with key file
- Upload project folder

### Step 5: Install Application Dependencies

On EC2 instance:

```bash
# Navigate to project
cd /home/ubuntu/fixit-tech

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install gunicorn (production WSGI server)
pip install gunicorn
```

### Step 6: Configure Environment Variables

```bash
# Edit .env file
nano app/.env
```

Add/update:
```env
JWT_SECRET=your-production-secret-key-change-this
GROQ_API_KEY=your-groq-api-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
MAIL_FROM=your-email@gmail.com
```

Save: `CTRL+X`, then `Y`, then `Enter`

### Step 7: Initialize Database

```bash
# Test run to initialize database
python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8081

# Press CTRL+C after you see:
# ✅ Database tables initialized successfully
# ✅ Default admin created
```

### Step 8: Configure Gunicorn Service

Create systemd service file:

```bash
sudo nano /etc/systemd/system/fixit-tech.service
```

Add this content:

```ini
[Unit]
Description=FixIt Tech Solutions FastAPI Application
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/fixit-tech
Environment="PATH=/home/ubuntu/fixit-tech/venv/bin"
ExecStart=/home/ubuntu/fixit-tech/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8081

[Install]
WantedBy=multi-user.target
```

Save and enable service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable fixit-tech

# Start service
sudo systemctl start fixit-tech

# Check status
sudo systemctl status fixit-tech
```

### Step 9: Configure Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/fixit-tech
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name <your-public-ip>;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site and restart Nginx:

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/fixit-tech /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Enable Nginx on boot
sudo systemctl enable nginx
```

### Step 10: Test Deployment

Open browser and visit:
- **http://<your-public-ip>** - Should show home page
- **http://<your-public-ip>/docs** - API documentation
- **http://<your-public-ip>/static/login.html** - Login page

### Step 11: Verify Services

```bash
# Check application status
sudo systemctl status fixit-tech

# Check Nginx status
sudo systemctl status nginx

# View application logs
sudo journalctl -u fixit-tech -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## Option 2: Elastic Beanstalk Deployment

### Step 1: Install EB CLI

```bash
pip install awsebcli
```

### Step 2: Prepare Application

Create `.ebextensions` folder in project root:

```bash
mkdir .ebextensions
```

Create `01_flask.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app.main:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
```

### Step 3: Initialize EB Application

```bash
# From project root
eb init -p python-3.11 fixit-tech-app --region us-east-1

# Create environment
eb create fixit-tech-env

# Set environment variables
eb setenv JWT_SECRET=your-secret GROQ_API_KEY=your-key

# Deploy
eb deploy

# Open in browser
eb open
```

### Step 4: Monitor

```bash
# Check status
eb status

# View logs
eb logs

# SSH to instance
eb ssh
```

---

## Option 3: Docker + ECS Deployment

### Step 1: Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8081

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8081:8081"
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./fixit_tech.db:/app/fixit_tech.db
    restart: unless-stopped
```

### Step 3: Test Locally

```bash
# Build image
docker build -t fixit-tech .

# Run container
docker run -p 8081:8081 fixit-tech
```

### Step 4: Push to AWS ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name fixit-tech

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag fixit-tech:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/fixit-tech:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/fixit-tech:latest
```

### Step 5: Deploy to ECS

1. Go to ECS Console
2. Create Cluster (EC2 or Fargate)
3. Create Task Definition
4. Create Service
5. Configure Load Balancer

---

## Database Configuration

### Option 1: SQLite (Development/Small Scale)

- Already configured
- File stored on EC2 instance
- No additional setup needed
- **Limitations**: Single instance only

### Option 2: AWS RDS PostgreSQL (Production)

**Create RDS Instance:**

1. Go to RDS Console
2. Create database:
   - Engine: PostgreSQL 14
   - Template: Free tier
   - DB instance: db.t2.micro
   - Storage: 20GB
   - Username: admin
   - Password: (set strong password)
   - Public access: No
   - VPC: Same as EC2
   - Security group: Allow PostgreSQL (5432) from EC2 security group

3. Wait for creation (10-15 minutes)

4. Get endpoint: `fixit-tech-db.xxxx.us-east-1.rds.amazonaws.com`

**Update Application:**

Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

Update `app/database.py`:
```python
# Change from SQLite
# SQLALCHEMY_DATABASE_URL = "sqlite:///./fixit_tech.db"

# To PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://admin:password@<rds-endpoint>:5432/fixittech"
```

Update `.env`:
```env
DATABASE_URL=postgresql://admin:password@<rds-endpoint>:5432/fixittech
```

Restart application:
```bash
sudo systemctl restart fixit-tech
```

---

## Security Configuration

### 1. Security Group Rules

**Application Security Group (fixit-tech-sg):**
```
Inbound:
- SSH (22) from My IP only
- HTTP (80) from 0.0.0.0/0
- HTTPS (443) from 0.0.0.0/0
- Port 8081 from 0.0.0.0/0 (testing only, remove in production)

Outbound:
- All traffic
```

**RDS Security Group (if using):**
```
Inbound:
- PostgreSQL (5432) from Application Security Group only

Outbound:
- Not needed
```

### 2. IAM Roles

Create IAM role for EC2:
- CloudWatchLogsFullAccess
- AmazonS3ReadOnlyAccess (if using S3)

Attach to EC2 instance.

### 3. Environment Variables

Never commit sensitive data:
```bash
# Add to .gitignore
app/.env
*.db
__pycache__/
venv/
```

### 4. Firewall

```bash
# Enable UFW firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### 5. SSL Certificate

After domain setup, install Let's Encrypt:

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already setup by certbot)
sudo certbot renew --dry-run
```

---

## Domain and SSL Setup

### 1. Register Domain

Options:
- AWS Route 53
- Namecheap
- GoDaddy
- Google Domains

### 2. Configure Route 53

```bash
# Create hosted zone
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)

# Create A record pointing to EC2 Elastic IP
# Use Route 53 console or CLI
```

### 3. Allocate Elastic IP

```bash
# Allocate Elastic IP
aws ec2 allocate-address

# Associate with instance
aws ec2 associate-address --instance-id <instance-id> --allocation-id <eip-allocation-id>
```

### 4. Update Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/fixit-tech
```

Update `server_name`:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## Monitoring and Logging

### 1. CloudWatch Agent

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard

# Start agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### 2. Application Logging

Update `app/main.py` to add logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/fixit-tech/app.log'),
        logging.StreamHandler()
    ]
)
```

Create log directory:
```bash
sudo mkdir -p /var/log/fixit-tech
sudo chown ubuntu:ubuntu /var/log/fixit-tech
```

### 3. Log Rotation

```bash
sudo nano /etc/logrotate.d/fixit-tech
```

Add:
```
/var/log/fixit-tech/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
}
```

---

## Cost Estimation

### Free Tier Usage (First 12 Months)

| Service | Free Tier | Estimated Cost After |
|---------|-----------|---------------------|
| EC2 t2.micro | 750 hours/month | $8-10/month |
| RDS db.t2.micro | 750 hours/month | $15-20/month |
| Data Transfer | 1GB out | $0.09/GB |
| Elastic IP | Free when attached | $0 |
| S3 Storage | 5GB | $0.023/GB |
| **Total** | **$0 for 12 months** | **~$25-30/month** |

### Cost Optimization Tips

1. **Stop instances when not in use** (development)
2. **Use Reserved Instances** (production, 1-year commitment saves 30-40%)
3. **Enable auto-scaling** only when needed
4. **Monitor with AWS Cost Explorer**
5. **Set up billing alerts**

---

## Troubleshooting

### Application Not Starting

```bash
# Check service status
sudo systemctl status fixit-tech

# View full logs
sudo journalctl -u fixit-tech -n 100 --no-pager

# Check for port conflicts
sudo netstat -tulpn | grep 8081

# Test manually
cd /home/ubuntu/fixit-tech
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8081
```

### Database Connection Errors

```bash
# For RDS, test connection
telnet <rds-endpoint> 5432

# Check security groups
aws ec2 describe-security-groups --group-ids <sg-id>

# Verify environment variables
cat app/.env
```

### Nginx 502 Bad Gateway

```bash
# Check if app is running
sudo systemctl status fixit-tech

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Verify Nginx config
sudo nginx -t

# Restart services
sudo systemctl restart fixit-tech nginx
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew --nginx

# Check certificate status
sudo certbot certificates

# Test SSL configuration
openssl s_client -connect yourdomain.com:443
```

### High CPU Usage

```bash
# Check processes
top
htop

# Check application logs for errors
sudo journalctl -u fixit-tech -f

# Consider upgrading instance type or adding auto-scaling
```

### Out of Memory

```bash
# Check memory usage
free -h

# Add swap space
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Can't Connect via SSH

```bash
# Check security group allows SSH from your IP
# Verify key file permissions
chmod 400 fixit-tech-key.pem

# Check instance status in AWS console
# Try stopping and starting instance (not rebooting)
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] AWS account created and configured
- [ ] IAM user with appropriate permissions
- [ ] AWS CLI installed and configured
- [ ] EC2 key pair created and downloaded
- [ ] Security groups configured
- [ ] Project files ready

### EC2 Deployment

- [ ] EC2 instance launched and running
- [ ] Successfully connected via SSH
- [ ] Python 3.11 installed
- [ ] Application files uploaded
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] Gunicorn service configured and running
- [ ] Nginx installed and configured
- [ ] Application accessible via public IP

### Production Readiness

- [ ] RDS database setup (if using)
- [ ] Domain name configured
- [ ] SSL certificate installed
- [ ] Firewall rules configured
- [ ] CloudWatch monitoring setup
- [ ] Log rotation configured
- [ ] Backup strategy implemented
- [ ] Auto-scaling configured (if needed)
- [ ] Load balancer setup (if needed)
- [ ] CI/CD pipeline setup (optional)

---

## Maintenance Commands

### Update Application

```bash
# SSH to EC2
ssh -i fixit-tech-key.pem ubuntu@<public-ip>

# Navigate to project
cd /home/ubuntu/fixit-tech

# Pull latest changes (if using Git)
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Restart application
sudo systemctl restart fixit-tech

# Check status
sudo systemctl status fixit-tech
```

### Backup Database

**SQLite:**
```bash
# Create backup
cp /home/ubuntu/fixit-tech/fixit_tech.db /home/ubuntu/backups/fixit_tech_$(date +%Y%m%d).db

# Download to local
scp -i fixit-tech-key.pem ubuntu@<public-ip>:/home/ubuntu/backups/*.db ./backups/
```

**PostgreSQL (RDS):**
```bash
# Create snapshot in RDS console
# Or use automated backups (enabled by default)
```

### Monitor Resources

```bash
# CPU and Memory
htop

# Disk usage
df -h

# Network connections
sudo netstat -tulpn

# Active connections to app
sudo netstat -an | grep 8081 | wc -l
```

---

## Additional Resources

### AWS Documentation

- EC2: https://docs.aws.amazon.com/ec2/
- RDS: https://docs.aws.amazon.com/rds/
- Elastic Beanstalk: https://docs.aws.amazon.com/elasticbeanstalk/
- ECS: https://docs.aws.amazon.com/ecs/

### Security Best Practices

- Enable MFA on AWS account
- Use IAM roles instead of access keys
- Regularly rotate credentials
- Keep systems updated
- Monitor CloudTrail logs
- Use AWS GuardDuty for threat detection

### Performance Optimization

- Enable caching (Redis/ElastiCache)
- Use CloudFront CDN for static files
- Implement database connection pooling
- Add indexes to frequently queried columns
- Monitor with APM tools (New Relic, Datadog)

---

## Support and Next Steps

### After Successful Deployment

1. **Test all features** thoroughly
2. **Set up monitoring alerts**
3. **Document your configuration**
4. **Plan backup strategy**
5. **Consider CI/CD pipeline**

### For Production

1. **Use RDS instead of SQLite**
2. **Implement auto-scaling**
3. **Add load balancer**
4. **Set up staging environment**
5. **Implement proper logging**
6. **Add performance monitoring**
7. **Regular security audits**

---

*Document Version: 1.0*  
*Last Updated: December 2025*  
*Course: CS 623 - Cloud Computing*  
*Deployment Target: AWS Cloud Platform*
