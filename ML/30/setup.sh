#!/bin/bash

# Setup script for Ubuntu droplet

echo "Setting up trading environment..."

# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Create systemd service for auto-start (optional)
cat > trading.service << 'EOF'
[Unit]
Description=HYPE Trading Algorithm
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/auto30
Environment="PATH=/root/auto30/venv/bin"
ExecStart=/root/auto30/venv/bin/python /root/auto30/30s.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Setup complete!"
echo "To run: source venv/bin/activate && python 30s.py"
echo "To install as service: sudo cp trading.service /etc/systemd/system/ && sudo systemctl enable trading"