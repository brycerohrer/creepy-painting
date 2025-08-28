# Face Tracker with Servo Control

A Python application that tracks faces in real-time and controls a servo motor to follow faces horizontally. Perfect for creating automated camera mounts, security systems, or interactive displays.

## Features

- **Real-time face detection** using OpenCV's Haar Cascade Classifier
- **Servo motor control** for horizontal face tracking
- **Smooth servo movement** with configurable smoothing and speed limits
- **Manual servo control** with slider and center button
- **Modern PyQt5 user interface** with servo control panel
- **Live video feed** with face detection visualization
- **Center line reference** to show tracking alignment
- **Hardware simulation mode** for development without physical hardware

## Hardware Requirements

### For Raspberry Pi (Recommended)
- **Raspberry Pi** (3B+, 4, or newer)
- **Servo motor** (SG90, MG996R, or similar)
- **Webcam** (USB or Pi Camera)
- **Power supply** for servo (5V, 1A+ recommended)
- **Breadboard and jumper wires**

### For Other Systems
- **Webcam**
- **USB servo controller** (if not using GPIO)
- **Power supply** for servo

## Circuit Setup

### Raspberry Pi GPIO Connection
```
Servo Signal (Orange/Yellow) → GPIO 18 (configurable)
Servo Power (Red) → 5V
Servo Ground (Brown/Black) → GND
```

**⚠️ Important**: Never power servos directly from Pi's 5V pin for high-current servos. Use external power supply and common ground.

### Alternative: USB Servo Controller
If not using Raspberry Pi GPIO, you can use:
- **Pololu Maestro** servo controller
- **Adafruit PWM** servo driver
- **Arduino** with servo library

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements_servo.txt
```

### 2. Hardware Setup
- Connect servo to GPIO 18 (or modify `pin` parameter in code)
- Ensure proper power supply for servo
- Connect webcam

### 3. Run Application
```bash
python face_tracker_servo.py
```

## Usage

### Basic Operation
1. **Start the application** - servo will center automatically
2. **Click "Start Tracking"** - face detection and servo tracking begin
3. **Move your face** - servo will follow horizontally
4. **Click "Stop Tracking"** - stop tracking and center servo

### Manual Control
- **Angle Slider**: Manually control servo position (0°-180°)
- **Center Button**: Return servo to center position (90°)
- **Real-time Updates**: See current servo angle during tracking

### Servo Configuration
Modify these parameters in the `ServoController` class:
```python
self.smoothing_factor = 0.3    # Movement smoothness (0.1-0.9)
self.dead_zone = 20           # Pixels from center to ignore
self.max_speed = 2            # Maximum degrees per frame
self.min_angle = 0            # Minimum servo angle
self.max_angle = 180          # Maximum servo angle
self.center_angle = 90        # Center position
```

## How It Works

### Face Detection
- Uses OpenCV's Haar Cascade Classifier
- Detects faces in real-time video stream
- Identifies largest face (closest to camera)

### Servo Control Algorithm
1. **Calculate face center** relative to frame center
2. **Apply dead zone** to prevent jitter
3. **Map offset to servo angle** using proportional control
4. **Apply smoothing** for fluid movement
5. **Limit speed** to prevent jerky motion
6. **Send PWM signal** to servo

### Tracking Logic
```
Face Left of Center → Servo turns Left
Face Right of Center → Servo turns Right
Face at Center → Servo stays centered
```

## Customization

### Different Servo Types
- **Standard Servos**: 0°-180° range (default)
- **Continuous Rotation**: Modify for 360° movement
- **High Torque**: Adjust power requirements

### Multiple Servos
Add vertical tracking by:
1. Creating second `ServoController` instance
2. Connecting to different GPIO pin
3. Modifying tracking logic for Y-axis movement

### Advanced Features
- **Face ID tracking** for multiple people
- **Predictive movement** using velocity estimation
- **Smooth acceleration/deceleration** curves
- **Calibration routines** for servo positioning

## Troubleshooting

### Servo Issues
- **Jittery movement**: Increase `smoothing_factor` or decrease `max_speed`
- **Not responding**: Check power supply and connections
- **Wrong range**: Adjust `min_angle` and `max_angle`
- **Overheating**: Reduce update frequency or use external power

### Performance Issues
- **Slow tracking**: Decrease `smoothing_factor` or increase `max_speed`
- **High CPU usage**: Increase `msleep()` delay in tracking loop
- **Camera lag**: Check webcam resolution and frame rate

### Hardware Issues
- **GPIO errors**: Ensure proper permissions (`sudo` or GPIO group)
- **Power issues**: Use external 5V supply for servos
- **Connection problems**: Check wiring and breadboard connections

## Safety Considerations

- **Never touch moving servo** while powered
- **Use appropriate power supply** for servo requirements
- **Secure mounting** to prevent servo from falling
- **Emergency stop** button for production systems
- **Limit servo range** to prevent damage

## Development Mode

The application automatically detects if hardware is available:
- **With hardware**: Full servo control and tracking
- **Without hardware**: Simulation mode with console output

This allows development and testing on any system before deploying to hardware.

## License

This project is open source and available under the MIT License. 