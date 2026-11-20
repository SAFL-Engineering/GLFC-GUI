#!/bin/bash

# Systemd Python Service Installer Script
# Make sure to run this script with sudo!

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# ==========================================
# CONFIGURATION - EDIT THESE VARIABLES
# ==========================================
SERVICE_NAME="GLFC_GUI"
SCRIPT_PATH="/home/pi/Documents/Github/GLFC-GUI/GLFC_GUI_v0.py"
PYTHON_PATH="/home/pi/Documents/Github/GLFC-GUI/GLFC-GUI/bin/python3"
RUN_USER="pi"
WORK_DIR="/home/pi/Documents/Github/GLFC-GUI"
# ==========================================

SERVICE_FILE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

echo "Creating service file at ${SERVICE_FILE_PATH}..."

cat <<EOF > "$SERVICE_FILE_PATH"
[Unit]
Description=Python Script Service (${SERVICE_NAME})
After=network.target

[Service]
ExecStart=${PYTHON_PATH} ${SCRIPT_PATH}
WorkingDirectory=${WORK_DIR}
Restart=always
RestartSec=3
User=${RUN_USER}
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Enabling service to start on boot..."
systemctl enable ${SERVICE_NAME}.service

echo "Starting the service..."
systemctl start ${SERVICE_NAME}.service

echo "----------------------------------------"
echo "Service '${SERVICE_NAME}' installed and started successfully!"
echo "Check its status with:  sudo systemctl status ${SERVICE_NAME}.service"
echo "View live logs with:    sudo journalctl -u ${SERVICE_NAME}.service -f"
