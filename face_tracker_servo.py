import sys
import cv2
import numpy as np
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSlider, QFrame)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor

# Servo control class
class ServoController:
    """Controls a servo motor for face tracking"""
    
    def __init__(self, pin=18, min_angle=0, max_angle=180, center_angle=90):
        self.pin = pin
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.center_angle = center_angle
        self.current_angle = center_angle
        
        # Servo control parameters
        self.smoothing_factor = 0.3  # Smoothing for movement (0.1 = very smooth, 0.9 = very responsive)
        self.dead_zone = 20  # Pixels from center to ignore (prevents jitter)
        self.max_speed = 2  # Maximum degrees per frame
        
        # Initialize servo (if using GPIO)
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            self.servo = GPIO.PWM(self.pin, 50)  # 50Hz PWM
            self.servo.start(0)
            self.hardware_available = True
            print(f"Hardware servo initialized on pin {self.pin}")
        except ImportError:
            # Fallback for development/testing without hardware
            self.hardware_available = False
            print("Hardware servo not available - running in simulation mode")
    
    def set_angle(self, angle):
        """Set servo to specific angle"""
        # Clamp angle to valid range
        angle = max(self.min_angle, min(self.max_angle, angle))
        
        if self.hardware_available:
            # Convert angle to duty cycle (0-100)
            duty_cycle = (angle / 180) * 10 + 2.5  # 2.5% = 0°, 12.5% = 180°
            self.servo.ChangeDutyCycle(duty_cycle)
            time.sleep(0.1)  # Allow servo to reach position
            self.servo.ChangeDutyCycle(0)  # Stop PWM to prevent jitter
        else:
            # Simulation mode
            print(f"Servo simulation: Moving to {angle}°")
        
        self.current_angle = angle
    
    def track_face(self, face_x, face_y, frame_width, frame_height):
        """Track face by adjusting servo angle"""
        # Calculate center of frame
        frame_center_x = frame_width // 2
        
        # Calculate horizontal offset from center
        offset_x = face_x - frame_center_x
        
        # Apply dead zone to prevent jitter
        if abs(offset_x) < self.dead_zone:
            return
        
        # Calculate target angle based on offset
        # Map offset to servo angle range
        angle_change = (offset_x / frame_center_x) * (self.max_angle - self.min_angle) * 0.5
        
        # Calculate new target angle
        target_angle = self.center_angle - angle_change
        
        # Apply smoothing and speed limiting
        angle_diff = target_angle - self.current_angle
        angle_diff = max(-self.max_speed, min(self.max_speed, angle_diff))
        
        new_angle = self.current_angle + (angle_diff * self.smoothing_factor)
        
        # Set new angle
        self.set_angle(new_angle)
    
    def center_servo(self):
        """Center the servo"""
        self.set_angle(self.center_angle)
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if self.hardware_available:
            self.servo.stop()
            import RPi.GPIO as GPIO
            GPIO.cleanup()

class FaceTrackerThread(QThread):
    """Thread for handling face detection and tracking"""
    frame_ready = pyqtSignal(np.ndarray, list)
    servo_angle_update = pyqtSignal(int)
    
    def __init__(self, servo_controller):
        super().__init__()
        self.running = False
        self.cap = None
        self.face_cascade = None
        self.servo_controller = servo_controller
        
    def run(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            return
            
        # Load face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Center servo at start
        self.servo_controller.center_servo()
        
        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                # Track largest face with servo
                if len(faces) > 0:
                    # Find largest face (closest to camera)
                    largest_face = max(faces, key=lambda x: x[2] * x[3])
                    x, y, w, h = largest_face
                    
                    # Calculate center of face
                    face_center_x = x + w // 2
                    face_center_y = y + h // 2
                    
                    # Track face with servo
                    self.servo_controller.track_face(face_center_x, face_center_y, frame.shape[1], frame.shape[0])
                    
                    # Emit servo angle for UI update
                    self.servo_angle_update.emit(self.servo_controller.current_angle)
                
                # Convert faces to list format for signal emission
                faces_list = faces.tolist() if len(faces) > 0 else []
                
                # Emit frame and detected faces
                self.frame_ready.emit(frame, faces_list)
                
            # Small delay to prevent overwhelming the system
            self.msleep(30)
    
    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.wait()

class FaceTrackerServoApp(QMainWindow):
    """Main application window for face tracking with servo control"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Tracker with Servo Control")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize servo controller
        self.servo_controller = ServoController()
        
        # Initialize variables
        self.tracker_thread = None
        self.is_tracking = False
        
        # Setup UI
        self.setup_ui()
        
        # Setup timer for UI updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Video display area
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                border-radius: 10px;
                background-color: #f0f0f0;
            }
        """)
        self.video_label.setText("Click 'Start Tracking' to begin")
        
        # Servo control panel
        servo_frame = QFrame()
        servo_frame.setFrameStyle(QFrame.Box)
        servo_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                background-color: #f8f9fa;
                padding: 10px;
            }
        """)
        
        servo_layout = QVBoxLayout(servo_frame)
        
        # Servo status
        servo_title = QLabel("Servo Control Panel")
        servo_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        servo_layout.addWidget(servo_title)
        
        # Current angle display
        self.angle_label = QLabel("Current Angle: 90°")
        self.angle_label.setStyleSheet("font-size: 14px; color: #666;")
        servo_layout.addWidget(self.angle_label)
        
        # Manual servo control
        manual_layout = QHBoxLayout()
        
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(0, 180)
        self.angle_slider.setValue(90)
        self.angle_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #ffffff;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #5c6bc0;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        self.angle_slider.valueChanged.connect(self.on_angle_slider_changed)
        
        self.center_button = QPushButton("Center Servo")
        self.center_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.center_button.clicked.connect(self.center_servo)
        
        manual_layout.addWidget(QLabel("Manual Control:"))
        manual_layout.addWidget(self.angle_slider)
        manual_layout.addWidget(self.center_button)
        servo_layout.addLayout(manual_layout)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Tracking")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.start_button.clicked.connect(self.toggle_tracking)
        
        self.stop_button = QPushButton("Stop Tracking")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
        """)
        self.stop_button.clicked.connect(self.stop_tracking)
        self.stop_button.setEnabled(False)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addStretch()
        
        # Status display
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 10px;
                background-color: #e8f5e8;
                border-radius: 5px;
            }
        """)
        
        # Face count display
        self.face_count_label = QLabel("Faces Detected: 0")
        self.face_count_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                padding: 5px;
            }
        """)
        
        # Add widgets to main layout
        main_layout.addWidget(self.video_label)
        main_layout.addWidget(servo_frame)
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.face_count_label)
        
    def on_angle_slider_changed(self, value):
        """Handle manual servo angle changes"""
        self.servo_controller.set_angle(value)
        self.angle_label.setText(f"Current Angle: {value}°")
    
    def center_servo(self):
        """Center the servo manually"""
        self.servo_controller.center_servo()
        self.angle_slider.setValue(90)
        self.angle_label.setText("Current Angle: 90°")
    
    def toggle_tracking(self):
        """Toggle face tracking on/off"""
        if not self.is_tracking:
            self.start_tracking()
        else:
            self.stop_tracking()
    
    def start_tracking(self):
        """Start face tracking"""
        self.tracker_thread = FaceTrackerThread(self.servo_controller)
        self.tracker_thread.frame_ready.connect(self.process_frame)
        self.tracker_thread.servo_angle_update.connect(self.update_servo_angle)
        self.tracker_thread.start()
        
        self.is_tracking = True
        self.start_button.setText("Stop Tracking")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Status: Tracking Active")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 10px;
                background-color: #fff3cd;
                border-radius: 5px;
            }
        """)
        
        # Start status update timer
        self.update_timer.start(1000)  # Update every second
    
    def stop_tracking(self):
        """Stop face tracking"""
        if self.tracker_thread:
            self.tracker_thread.stop()
            self.tracker_thread = None
        
        self.is_tracking = False
        self.start_button.setText("Start Tracking")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Status: Stopped")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 10px;
                background-color: #f8d7da;
                border-radius: 5px;
            }
        """)
        
        # Clear video display
        self.video_label.setText("Click 'Start Tracking' to begin")
        self.face_count_label.setText("Faces Detected: 0")
        
        # Stop status update timer
        self.update_timer.stop()
    
    def process_frame(self, frame, faces):
        """Process the video frame and detected faces"""
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f'Face', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Draw center line for reference
        center_x = frame.shape[1] // 2
        cv2.line(frame, (center_x, 0), (center_x, frame.shape[0]), (255, 0, 0), 2)
        
        # Convert frame to Qt format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        # Scale pixmap to fit the label while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)
        
        # Update face count
        self.face_count_label.setText(f"Faces Detected: {len(faces)}")
    
    def update_servo_angle(self, angle):
        """Update servo angle display from tracking thread"""
        self.angle_label.setText(f"Current Angle: {angle}°")
        # Don't update slider during tracking to avoid conflicts
    
    def update_status(self):
        """Update status display"""
        if self.is_tracking and self.tracker_thread and self.tracker_thread.isRunning():
            self.status_label.setText("Status: Tracking Active - Camera Running")
        elif self.is_tracking:
            self.status_label.setText("Status: Tracking Active - Camera Starting...")
    
    def closeEvent(self, event):
        """Handle application close event"""
        self.stop_tracking()
        self.servo_controller.cleanup()
        event.accept()

def main():
    """Main function to run the application"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = FaceTrackerServoApp()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 