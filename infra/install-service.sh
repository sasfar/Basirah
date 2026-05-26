#!/bin/bash

# Basirah Service Installation Script

set -e

echo "🌙 Installing Basirah as a systemd service..."

# Copy service file
echo "📝 Copying service file..."
sudo cp /home/syeddgx/Projects/Basirah/infra/basirah.service /etc/systemd/system/

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Enable service
echo "✅ Enabling Basirah service..."
sudo systemctl enable basirah.service

echo ""
echo "✅ Installation complete!"
echo ""
echo "Available commands:"
echo "  sudo systemctl start basirah    # Start Basirah"
echo "  sudo systemctl stop basirah     # Stop Basirah"
echo "  sudo systemctl restart basirah  # Restart Basirah"
echo "  sudo systemctl status basirah   # Check status"
echo "  sudo journalctl -u basirah -f   # View logs"
echo ""
echo "Basirah will now start automatically on boot."
echo ""
echo "Access URLs:"
echo "  - Web UI: http://192.168.1.147"
echo "  - API: http://192.168.1.147:8081"
echo ""
