# Quick Start Deployment Guide

## 🚀 Deploy to AWS in 30 Minutes

Follow these steps to deploy FixIt Tech Solutions to AWS EC2.

---

## Part 1: AWS Console Setup (10 minutes)

### 1. Login to AWS
- Go to: https://console.aws.amazon.com/
- Login with your AWS account

### 2. Launch EC2 Instance

1. **Go to EC2 Dashboard**
   - Search "EC2" in AWS console
   - Click "Launch Instance"

2. **Configure Instance**
   ```
   Name: fixit-tech-server
   AMI: Ubuntu Server 22.04 LTS (Free Tier)
   Instance Type: t2.micro (Free Tier)
   ```

3. **Create Key Pair**
   - Click "Create new key pair"
   - Name: `fixit-tech-key`
   - Type: RSA
   - Format: .pem (download and SAVE THIS FILE!)

4. **Network Settings**
   - Check "Allow SSH traffic from" → My IP
   - Check "Allow HTTPS traffic from the internet"
   - Check "Allow HTTP traffic from the internet"
   
5. **Add Custom Security Rule**
   - Click "Add security group rule"
   - Type: Custom TCP
   - Port: 8081
   - Source: 0.0.0.0/0

6. **Storage**: 8 GB (default - Free Tier)

7. **Click "Launch Instance"**

8. **Wait 2-3 minutes** for instance to start

9. **Get Public IP**
   - Select your instance
   - Copy "Public IPv4 address" (e.g., 3.15.123.45)
   - SAVE THIS IP ADDRESS!

---

## Part 2: Connect to EC2 (5 minutes)

### Windows Users:

**Option A: PowerShell/CMD**
```powershell
# Navigate to where you saved the key file
cd Downloads

# Set proper permissions (may not be needed on Windows)
icacls fixit-tech-key.pem /inheritance:r /grant:r "%USERNAME%:R"

# Connect via SSH
ssh -i fixit-tech-key.pem ubuntu@YOUR_PUBLIC_IP
```

**Option B: Use PuTTY**
1. Download PuTTY from: https://www.putty.org/
2. Convert .pem to .ppk using PuTTYgen
3. Connect using PuTTY with the .ppk file

### Mac/Linux Users:
```bash
# Set key permissions
chmod 400 ~/Downloads/fixit-tech-key.pem

# Connect via SSH
ssh -i ~/Downloads/fixit-tech-key.pem ubuntu@YOUR_PUBLIC_IP
```

**When asked "Are you sure you want to continue connecting?"**
Type: `yes` and press Enter

---

## Part 3: Deploy Application (15 minutes)

Once connected to EC2, run these commands:

### 1. Download and Run Setup Script
```bash
# Download the deployment script
curl -O https://raw.githubusercontent.com/vvskad1/Cloud-Computing-Final-Project-by4412/main/deploy_ec2.sh

# Make it executable
chmod +x deploy_ec2.sh

# Run the script
./deploy_ec2.sh
```

**Script will install:**
- Python 3.11
- Nginx
- Git
- Clone the repository
- Setup virtual environment
- Install all dependencies

### 2. Configure Environment Variables
```bash
# Navigate to project
cd /home/ubuntu/fixit-tech

# Edit environment file
nano app/.env
```

**Update these values:**
```env
JWT_SECRET=your-random-secret-key-change-this-now
GROQ_API_KEY=your-groq-api-key-from-console.groq.com
```

**Save and exit:**
- Press `CTRL + X`
- Press `Y`
- Press `Enter`

### 3. Test the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Test run
uvicorn app.main:app --host 0.0.0.0 --port 8081
```

**You should see:**
```
✅ Database tables initialized successfully
✅ Default admin created (username: admin, password: admin123)
INFO:     Uvicorn running on http://0.0.0.0:8081
```

**Test in browser:**
- Open: `http://YOUR_PUBLIC_IP:8081`
- You should see the homepage!

**Stop the test server:**
- Press `CTRL + C`

### 4. Setup Production Server (Gunicorn)
```bash
# Create systemd service file
sudo nano /etc/systemd/system/fixit-tech.service
```

**Paste this content:**
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

**Save:** `CTRL + X`, `Y`, `Enter`

**Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable fixit-tech
sudo systemctl start fixit-tech
sudo systemctl status fixit-tech
```

**Should show:** "active (running)" in green

### 5. Setup Nginx Reverse Proxy
```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/fixit-tech
```

**Paste this content (replace YOUR_PUBLIC_IP):**
```nginx
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;

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

**Save:** `CTRL + X`, `Y`, `Enter`

**Enable site and restart Nginx:**
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/fixit-tech /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## Part 4: Access Your Application! 🎉

Open your browser and visit:

- **Homepage:** `http://YOUR_PUBLIC_IP`
- **Login:** `http://YOUR_PUBLIC_IP/static/login.html`
- **API Docs:** `http://YOUR_PUBLIC_IP/docs`

### Default Admin Credentials:
- Username: `admin`
- Password: `admin123`

### Create Customer Account:
- Go to: `http://YOUR_PUBLIC_IP/static/signup.html`

---

## Verification Checklist

✅ EC2 instance running  
✅ Application service active: `sudo systemctl status fixit-tech`  
✅ Nginx running: `sudo systemctl status nginx`  
✅ Homepage loads  
✅ Admin login works  
✅ Customer signup works  
✅ API documentation accessible  

---

## Common Commands

### View Application Logs
```bash
sudo journalctl -u fixit-tech -f
```

### Restart Application
```bash
sudo systemctl restart fixit-tech
```

### Restart Nginx
```bash
sudo systemctl restart nginx
```

### Check Status
```bash
sudo systemctl status fixit-tech
sudo systemctl status nginx
```

### Update Application
```bash
cd /home/ubuntu/fixit-tech
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fixit-tech
```

---

## Troubleshooting

### Can't connect via SSH?
- Check security group allows SSH (port 22) from your IP
- Verify key file permissions: `chmod 400 fixit-tech-key.pem`

### Application not starting?
```bash
# Check logs
sudo journalctl -u fixit-tech -n 50 --no-pager

# Test manually
cd /home/ubuntu/fixit-tech
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8081
```

### Nginx 502 error?
```bash
# Check if app is running
sudo systemctl status fixit-tech

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Port 8081 blocked?
- Check EC2 security group includes port 8081
- Or access via port 80 (Nginx proxy)

---

## Your Deployment is Complete! 🎉

**Your app is now live at:** `http://YOUR_PUBLIC_IP`

### Next Steps (Optional):

1. **Get a Domain Name**
   - Register domain (Namecheap, GoDaddy, Route 53)
   - Point domain to your EC2 IP

2. **Add SSL Certificate**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

3. **Setup Monitoring**
   - Configure CloudWatch
   - Set up billing alerts

4. **Regular Backups**
   ```bash
   # Backup database
   cp /home/ubuntu/fixit-tech/fixit_tech.db ~/backups/
   ```

---

**Need Help?**
- Check `AWS_DEPLOYMENT_GUIDE.md` for detailed troubleshooting
- Review logs: `sudo journalctl -u fixit-tech -f`

**Costs:**
- First 12 months: FREE (AWS Free Tier)
- After: ~$8-10/month (t2.micro EC2)

🎊 Congratulations on your successful deployment!
