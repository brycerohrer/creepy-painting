#!/bin/bash
# Raspberry Pi USB Network Setup Script
# This script configures your Pi for USB networking with VS Code

echo "🔧 Setting up Raspberry Pi for USB networking..."
echo "================================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Backup original config
echo "📋 Backing up original config.txt..."
cp /boot/config.txt /boot/config.txt.backup

# Add USB networking to config.txt
echo "🔌 Adding USB networking to config.txt..."
cat >> /boot/config.txt << EOF

# USB Networking Configuration
dtoverlay=dwc2
dtoverlay=libcomposite
EOF

# Create USB network device configuration
echo "🌐 Creating USB network configuration..."
cat > /etc/systemd/system/usb0.netdev << EOF
[NetDev]
Name=usb0
Kind=bridge
EOF

# Create USB network interface configuration
echo "🔧 Creating network interface configuration..."
cat > /etc/systemd/system/usb0.network << EOF
[Match]
Name=usb0

[Network]
Address=192.168.42.1/24
DHCPServer=yes
EOF

# Enable required services
echo "🚀 Enabling required services..."
systemctl enable usb0.netdev
systemctl enable usb0.network
systemctl enable systemd-networkd

# Install required packages
echo "📦 Installing required packages..."
apt update
apt install -y bridge-utils dnsmasq

# Configure dnsmasq for DHCP
echo "⚙️ Configuring DHCP server..."
cat > /etc/dnsmasq.conf << EOF
interface=usb0
dhcp-range=192.168.42.2,192.168.42.20,255.255.255.0,24h
dhcp-option=3,192.168.42.1
dhcp-option=6,192.168.42.1
EOF

# Enable dnsmasq
systemctl enable dnsmasq

# Create startup script
echo "📝 Creating startup script..."
cat > /usr/local/bin/start-usb-network.sh << 'EOF'
#!/bin/bash
# Start USB network interface

# Create USB gadget
mkdir -p /sys/kernel/config/usb_gadget/g1
cd /sys/kernel/config/usb_gadget/g1

# Set vendor and product IDs
echo 0x1d6b > idVendor
echo 0x0104 > idProduct

# Set strings
mkdir -p strings/0x409
echo "Raspberry Pi" > strings/0x409/manufacturer
echo "USB Network Device" > strings/0x409/product

# Create configuration
mkdir -p configs/c.1/strings/0x409
echo "RNDIS" > configs/c.1/strings/0x409/configuration

# Add RNDIS function
mkdir -p functions/rndis.usb0

# Add function to configuration
ln -s functions/rndis.usb0 configs/c.1/

# Enable gadget
echo 1 > UDC
EOF

chmod +x /usr/local/bin/start-usb-network.sh

# Add to systemd service
cat > /etc/systemd/system/usb-gadget.service << EOF
[Unit]
Description=USB Gadget Network
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/start-usb-network.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl enable usb-gadget.service

# Create connection info file
echo "📄 Creating connection information..."
cat > /home/pi/usb_connection_info.txt << EOF
===============================================
Raspberry Pi USB Network Setup Complete!
===============================================

Connection Details:
- IP Address: 192.168.42.1
- Username: pi
- Password: [your pi password]

VS Code Connection:
1. Install "Remote - SSH" extension
2. Press Ctrl+Shift+P
3. Type "Remote-SSH: Connect to Host"
4. Enter: pi@192.168.42.1
5. Enter your password when prompted

Troubleshooting:
- If connection fails, try: ping 192.168.42.1
- Check USB cable connection
- Ensure Pi is powered on
- Try different USB ports

Network Status:
- Check with: ip addr show usb0
- Restart service: sudo systemctl restart usb-gadget.service
===============================================
EOF

chown pi:pi /home/pi/usb_connection_info.txt

echo ""
echo "✅ Setup complete! Please reboot your Pi:"
echo "   sudo reboot"
echo ""
echo "📋 Connection info saved to: /home/pi/usb_connection_info.txt"
echo ""
echo "🔌 After reboot, connect USB cable and use:"
echo "   pi@192.168.42.1"
echo ""
echo "🌐 Check network status with: ip addr show usb0" 