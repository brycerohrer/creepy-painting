@echo off
echo ================================================
echo Windows USB Network Setup for Raspberry Pi
echo ================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ❌ Please run as Administrator (Right-click -> Run as Administrator)
    pause
    exit /b 1
)

echo.
echo 🔧 Setting up USB network connection...
echo.

REM Create network adapter configuration
echo Creating network configuration...

REM Add static route to Pi
echo Adding route to Raspberry Pi (192.168.42.1)...
route add 192.168.42.0 mask 255.255.255.0 0.0.0.0 metric 1

REM Configure network adapter (if exists)
echo Configuring network adapter...
netsh interface ip set address "Ethernet" static 192.168.42.2 255.255.255.0 192.168.42.1

echo.
echo 📋 Connection Information:
echo ================================================
echo Pi IP Address: 192.168.42.1
echo PC IP Address: 192.168.42.2
echo Username: pi
echo.
echo 🔌 Next Steps:
echo 1. Connect USB cable to Raspberry Pi
echo 2. Wait for Pi to boot and establish connection
echo 3. Test connection: ping 192.168.42.1
echo 4. In VS Code: Connect to pi@192.168.42.1
echo.
echo 📚 VS Code Setup:
echo 1. Install "Remote - SSH" extension
echo 2. Press Ctrl+Shift+P
echo 3. Type "Remote-SSH: Connect to Host"
echo 4. Enter: pi@192.168.42.1
echo 5. Enter your Pi password when prompted
echo.
echo ================================================
echo.

REM Test connection
echo Testing connection to Raspberry Pi...
ping -n 1 192.168.42.1 >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Connection successful!
    echo You can now connect from VS Code
) else (
    echo ⚠️ Connection failed - Pi may not be ready yet
    echo Wait for Pi to boot and try again
)

echo.
pause 