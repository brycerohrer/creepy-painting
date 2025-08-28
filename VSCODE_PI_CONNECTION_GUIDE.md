# VS Code to Raspberry Pi USB Connection Guide

Connect to your Raspberry Pi directly from VS Code using a USB cable for seamless development and deployment.

## 🚀 Quick Start (3 Methods)

### Method 1: USB Network Connection (Recommended)
- **Pros**: Full network access, file transfer, terminal, debugging
- **Cons**: Requires Pi configuration
- **Best for**: Development, debugging, file management

### Method 2: USB Serial Connection
- **Pros**: Simple setup, reliable connection
- **Cons**: Limited to terminal access
- **Best for**: Basic development, troubleshooting

### Method 3: USB to Ethernet Bridge
- **Pros**: Plug-and-play, no Pi configuration
- **Cons**: Requires hardware adapter
- **Best for**: Quick setup, temporary connections

---

## 🔌 Method 1: USB Network Connection

### Step 1: Configure Raspberry Pi

1. **SSH into your Pi** (via WiFi or Ethernet)
2. **Download and run the setup script**:
   ```bash
   wget https://raw.githubusercontent.com/brycerohrer/creepy-painting/main/setup_pi_usb_network.sh
   chmod +x setup_pi_usb_network.sh
   sudo ./setup_pi_usb_network.sh
   ```

3. **Reboot your Pi**:
   ```bash
   sudo reboot
   ```

### Step 2: Configure Windows PC

1. **Run the Windows setup script as Administrator**:
   - Right-click `setup_windows_usb_network.bat`
   - Select "Run as Administrator"

2. **Connect USB cable** from Pi to PC

3. **Wait for connection** (Pi will appear as network device)

### Step 3: Connect from VS Code

1. **Install Remote-SSH extension** in VS Code
2. **Press `Ctrl+Shift+P`**
3. **Type "Remote-SSH: Connect to Host"**
4. **Enter**: `pi@192.168.42.1`
5. **Enter your Pi password**

---

## 📡 Method 2: USB Serial Connection

### Step 1: Enable Serial on Pi

```bash
# Edit config.txt
sudo nano /boot/config.txt

# Add these lines:
enable_uart=1
dtoverlay=disable-bt  # If you don't need Bluetooth

# Reboot
sudo reboot
```

### Step 2: Install Serial Tools

```bash
sudo apt update
sudo apt install minicom screen
```

### Step 3: Connect via Serial

```bash
# On Pi, get device info
ls -l /dev/ttyUSB* /dev/ttyACM*

# Connect using screen
screen /dev/ttyUSB0 115200
# or
minicom -D /dev/ttyUSB0 -b 115200
```

---

## 🔧 Method 3: USB to Ethernet Bridge

### Hardware Setup
1. **Connect USB-to-Ethernet adapter** to Pi
2. **Connect Ethernet cable** to PC
3. **Configure static IP** on both devices

### Network Configuration
```bash
# On Pi
sudo nano /etc/dhcpcd.conf

# Add static IP
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8
```

---

## 🎯 VS Code Setup

### Install Required Extensions
1. **Remote - SSH** (for network connections)
2. **Remote - Containers** (for container development)
3. **Python** (for Python development)
4. **C/C++** (if developing in C/C++)

### Connect to Pi
1. **Press `Ctrl+Shift+P`**
2. **Type "Remote-SSH: Connect to Host"**
3. **Enter connection string**:
   - Network: `pi@192.168.42.1`
   - Serial: `pi@/dev/ttyUSB0`
   - Ethernet: `pi@192.168.1.100`

### First Connection
- **Select platform**: Linux
- **Enter password**: Your Pi password
- **Wait for setup**: VS Code will install server

---

## 🧪 Testing Your Connection

### Test Network Connection
```bash
# On Windows
ping 192.168.42.1

# On Pi
ping 192.168.42.2
```

### Test SSH Connection
```bash
# From Windows
ssh pi@192.168.42.1
```

### Test VS Code Connection
1. **Open VS Code**
2. **Connect to Pi**
3. **Open terminal** (`Ctrl+`` `)
4. **Run**: `echo "Hello from Pi!"`

---

## 📁 Working with Files

### Open Folder on Pi
1. **Connect to Pi** in VS Code
2. **File → Open Folder**
3. **Navigate to project directory**
4. **Start coding!**

### File Transfer
- **Drag & Drop**: Files between PC and Pi
- **Copy/Paste**: Between VS Code windows
- **Terminal**: Use `scp` or `rsync`

---

## 🐍 Running Your Face Tracker

### Install Dependencies
```bash
# On Pi, in VS Code terminal
pip install -r requirements_servo.txt
```

### Test Servo (Simulation Mode)
```bash
python3 test_servo.py --simulation
```

### Run Full Application
```bash
python3 face_tracker_servo.py
```

### Hardware Mode
1. **Connect servo** to GPIO 18
2. **Connect webcam**
3. **Run application** - will automatically detect hardware

---

## 🔍 Troubleshooting

### Connection Issues
```bash
# Check Pi network status
ip addr show usb0

# Restart USB network service
sudo systemctl restart usb-gadget.service

# Check USB gadget status
ls /sys/kernel/config/usb_gadget/
```

### VS Code Issues
- **Reinstall Remote-SSH extension**
- **Clear SSH known_hosts**: Delete `~/.ssh/known_hosts`
- **Check firewall settings**

### Hardware Issues
- **Try different USB ports**
- **Check USB cable quality**
- **Verify Pi power supply**

---

## 🎉 What You Can Do Now

### Development Features
- ✅ **Real-time editing** on Pi from VS Code
- ✅ **Integrated terminal** access
- ✅ **File management** and transfer
- ✅ **Debugging** with breakpoints
- ✅ **Git integration** on Pi
- ✅ **Extension support** on Pi

### Face Tracker Features
- ✅ **Edit code** directly on Pi
- ✅ **Test servo** movements
- ✅ **Debug face detection**
- ✅ **Monitor performance**
- ✅ **Deploy updates** instantly

---

## 🚀 Next Steps

1. **Test basic connection** using ping
2. **Connect VS Code** to Pi
3. **Open your face tracker project**
4. **Install dependencies** on Pi
5. **Run and test** the application
6. **Connect servo hardware**
7. **Deploy and enjoy!**

---

## 📚 Additional Resources

- [VS Code Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)
- [Raspberry Pi USB Gadget](https://www.raspberrypi.org/documentation/linux/usage/gadget-mode.md)
- [SSH Configuration](https://www.raspberrypi.org/documentation/remote-access/ssh/)
- [GPIO Pinout](https://pinout.xyz/)

---

## 🆘 Need Help?

If you encounter issues:
1. **Check the troubleshooting section** above
2. **Verify all connections** and configurations
3. **Check Pi system logs**: `sudo journalctl -f`
4. **Test with simple commands** first
5. **Ensure proper power supply** for Pi

Happy coding! 🎯🐍 