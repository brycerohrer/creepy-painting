#!/usr/bin/env python3
"""
Raspberry Pi Pico Connection Checker
Detects if a Pico is connected and provides connection details
"""

import sys
import os
import platform
import subprocess
import time

class PicoDetector:
    """Detect Raspberry Pi Pico connections"""
    
    def __init__(self):
        self.os_type = platform.system()
        self.pico_found = False
        self.connection_info = {}
    
    def detect_windows(self):
        """Detect Pico on Windows"""
        try:
            # Check for Pico in device manager
            result = subprocess.run(
                ['powershell', 'Get-PnpDevice | Where-Object {$_.FriendlyName -like "*Pico*" -or $_.FriendlyName -like "*Raspberry*"}'],
                capture_output=True, text=True, shell=True
            )
            
            if result.stdout.strip():
                self.pico_found = True
                self.connection_info['windows_devices'] = result.stdout.strip()
            
            # Check COM ports
            result = subprocess.run(
                ['powershell', 'Get-PnpDevice | Where-Object {$_.Class -eq "Ports"}'],
                capture_output=True, text=True, shell=True
            )
            
            if result.stdout.strip():
                self.connection_info['com_ports'] = result.stdout.strip()
                
        except Exception as e:
            print(f"Windows detection error: {e}")
    
    def detect_linux(self):
        """Detect Pico on Linux"""
        try:
            # Check USB devices
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            if result.stdout:
                pico_lines = [line for line in result.stdout.split('\n') if 'pico' in line.lower() or 'raspberry' in line.lower()]
                if pico_lines:
                    self.pico_found = True
                    self.connection_info['usb_devices'] = pico_lines
            
            # Check serial devices
            serial_devices = []
            for device in ['/dev/ttyACM*', '/dev/ttyUSB*']:
                try:
                    result = subprocess.run(['ls', device], capture_output=True, text=True, shell=True)
                    if result.stdout.strip():
                        serial_devices.extend(result.stdout.strip().split('\n'))
                except:
                    pass
            
            if serial_devices:
                self.connection_info['serial_devices'] = serial_devices
                
        except Exception as e:
            print(f"Linux detection error: {e}")
    
    def detect_macos(self):
        """Detect Pico on macOS"""
        try:
            # Check USB devices
            result = subprocess.run(['system_profiler', 'SPUSBDataType'], capture_output=True, text=True)
            if result.stdout:
                pico_lines = [line for line in result.stdout.split('\n') if 'pico' in line.lower() or 'raspberry' in line.lower()]
                if pico_lines:
                    self.pico_found = True
                    self.connection_info['usb_devices'] = pico_lines
            
            # Check serial devices
            try:
                result = subprocess.run(['ls', '/dev/tty.usbmodem*', '/dev/tty.usbserial*'], 
                                      capture_output=True, text=True, shell=True)
                if result.stdout.strip():
                    self.connection_info['serial_devices'] = result.stdout.strip().split('\n')
            except:
                pass
                
        except Exception as e:
            print(f"macOS detection error: {e}")
    
    def detect(self):
        """Detect Pico based on operating system"""
        print(f"🔍 Detecting Raspberry Pi Pico on {self.os_type}...")
        print("=" * 50)
        
        if self.os_type == "Windows":
            self.detect_windows()
        elif self.os_type == "Linux":
            self.detect_linux()
        elif self.os_type == "Darwin":  # macOS
            self.detect_macos()
        else:
            print(f"❌ Unsupported operating system: {self.os_type}")
            return False
        
        return self.pico_found
    
    def test_connection(self):
        """Test if we can communicate with the Pico"""
        print("\n🧪 Testing Pico connection...")
        
        if not self.connection_info.get('serial_devices'):
            print("❌ No serial devices found to test")
            return False
        
        # Test first available serial device
        test_device = self.connection_info['serial_devices'][0]
        print(f"📡 Testing device: {test_device}")
        
        try:
            if self.os_type == "Windows":
                # Windows serial test
                result = subprocess.run(['mode', test_device], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    print(f"✅ Serial device {test_device} is accessible")
                    return True
                else:
                    print(f"❌ Serial device {test_device} is not accessible")
                    return False
            else:
                # Linux/macOS serial test
                result = subprocess.run(['stty', '-F', test_device], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Serial device {test_device} is accessible")
                    return True
                else:
                    print(f"❌ Serial device {test_device} is not accessible")
                    return False
                    
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def print_summary(self):
        """Print detection summary"""
        print("\n📋 Detection Summary")
        print("=" * 50)
        
        if self.pico_found:
            print("✅ Raspberry Pi Pico detected!")
        else:
            print("❌ Raspberry Pi Pico not found")
        
        print(f"\n🔧 Operating System: {self.os_type}")
        
        if self.connection_info:
            print("\n📡 Connection Details:")
            for key, value in self.connection_info.items():
                print(f"  {key}:")
                if isinstance(value, list):
                    for item in value:
                        print(f"    {item}")
                else:
                    print(f"    {value}")
        
        print("\n💡 Next Steps:")
        if self.pico_found:
            print("  - Pico is connected and detected")
            print("  - You can now program it or communicate via serial")
            print("  - Use the detected serial device for communication")
        else:
            print("  - Check USB cable connection")
            print("  - Ensure Pico is powered on")
            print("  - Try different USB ports")
            print("  - Check if Pico is in bootloader mode")

def main():
    """Main function"""
    print("🚀 Raspberry Pi Pico Connection Checker")
    print("=" * 50)
    
    detector = PicoDetector()
    
    # Detect Pico
    if detector.detect():
        print("✅ Pico detection completed")
        
        # Test connection
        connection_ok = detector.test_connection()
        
        # Print summary
        detector.print_summary()
        
        if connection_ok:
            print("\n🎉 Pico is ready for development!")
        else:
            print("\n⚠️ Pico detected but connection test failed")
    else:
        print("❌ Pico detection failed")
        detector.print_summary()

if __name__ == "__main__":
    main() 