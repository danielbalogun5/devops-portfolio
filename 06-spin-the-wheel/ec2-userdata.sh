#!/bin/bash
# EC2 User Data — auto-installs and starts Spin the Wheel on port 80
set -e

# System updates
yum update -y
yum install -y git python3 python3-pip

# Clone the portfolio repo (update URL to your actual GitHub repo)
git clone https://github.com/danielbalogun5/devops-portfolio.git /opt/spin-the-wheel
cd /opt/spin-the-wheel/06-spin-the-wheel

# Install dependencies
pip3 install -r requirements.txt

# Allow port 80 (run gunicorn on port 80 as root for simplicity)
# In production, use nginx reverse proxy
gunicorn --bind 0.0.0.0:80 --workers 2 --daemon --access-logfile /var/log/spin-wheel-access.log --error-logfile /var/log/spin-wheel-error.log app:app

echo "Spin the Wheel is running on port 80"
