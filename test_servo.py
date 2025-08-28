#!/usr/bin/env python3
"""
Simple servo test script for face tracker servo system
Tests basic servo movement and positioning
"""

import time
import sys

def test_servo_basic():
    """Test basic servo functionality"""
    print("Testing Servo Controller...")
    
    try:
        from face_tracker_servo import ServoController
        
        # Create servo controller
        servo = ServoController()
        
        print("✓ Servo controller created successfully")
        print(f"✓ Hardware available: {servo.hardware_available}")
        
        # Test basic movements
        print("\nTesting servo movements...")
        
        # Center position
        print("Moving to center (90°)...")
        servo.set_angle(90)
        time.sleep(1)
        
        # Left position
        print("Moving to left (0°)...")
        servo.set_angle(0)
        time.sleep(1)
        
        # Right position
        print("Moving to right (180°)...")
        servo.set_angle(180)
        time.sleep(1)
        
        # Back to center
        print("Moving back to center (90°)...")
        servo.set_angle(90)
        time.sleep(1)
        
        # Test smooth movement
        print("\nTesting smooth movement...")
        for angle in range(0, 181, 10):
            servo.set_angle(angle)
            time.sleep(0.1)
        
        # Back to center
        servo.set_angle(90)
        
        print("\n✓ All servo tests completed successfully!")
        
        # Cleanup
        servo.cleanup()
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure face_tracker_servo.py is in the same directory")
    except Exception as e:
        print(f"✗ Error during testing: {e}")

def test_servo_simulation():
    """Test servo in simulation mode"""
    print("Testing Servo Controller in Simulation Mode...")
    
    try:
        from face_tracker_servo import ServoController
        
        # Create servo controller (will run in simulation mode)
        servo = ServoController()
        
        print("✓ Servo controller created successfully")
        print(f"✓ Hardware available: {servo.hardware_available}")
        
        # Test movements (will show console output)
        print("\nTesting servo movements in simulation...")
        
        servo.set_angle(90)
        time.sleep(0.5)
        servo.set_angle(0)
        time.sleep(0.5)
        servo.set_angle(180)
        time.sleep(0.5)
        servo.set_angle(90)
        
        print("\n✓ Simulation tests completed successfully!")
        
        # Cleanup
        servo.cleanup()
        
    except Exception as e:
        print(f"✗ Error during simulation testing: {e}")

def main():
    """Main test function"""
    print("=" * 50)
    print("Servo Controller Test Suite")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--simulation":
        test_servo_simulation()
    else:
        test_servo_basic()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)

if __name__ == "__main__":
    main() 