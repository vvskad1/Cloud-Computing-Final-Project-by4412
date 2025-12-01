#!/bin/bash
# FixIt Tech Solutions - EC2 Setup Script
# Run this script on your EC2 instance after connecting via SSH

echo "=================================="
echo "FixIt Tech Solutions - AWS Deployment"
echo "=================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
echo "🐍 Installing Python 3.11..."
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install nginx -y

# Install Git
echo "📂 Installing Git..."
sudo apt install git -y

# Clone repository
echo "📥 Cloning repository..."
cd /home/ubuntu
git clone https://github.com/vvskad1/Cloud-Computing-Final-Project-by4412.git fixit-tech
cd fixit-tech

# Create virtual environment
echo "🔧 Setting up virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install Gunicorn
pip install gunicorn

# Setup environment file
echo "⚙️ Setting up environment variables..."
cp app/.env.example app/.env
echo "⚠️  IMPORTANT: Edit app/.env with your production secrets!"
echo "   Run: nano app/.env"

# Initialize database
echo "🗄️ Initializing database..."
python3.11 -c "from app.database import create_tables; create_tables()"

echo ""
echo "=================================="
echo "✅ Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit environment variables: nano app/.env"
echo "2. Test the application: uvicorn app.main:app --host 0.0.0.0 --port 8081"
echo "3. Follow AWS_DEPLOYMENT_GUIDE.md to setup Gunicorn and Nginx"
echo ""
