import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSlider, QFrame)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor

class FaceTrackerThread(QThread):
    """Thread for handling face detection and tracking"""
    frame_ready = pyqtSignal(np.ndarray, list)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.cap = None
        self.face_cascade = None
        
    def run(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            return
            
        # Load face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
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

class FaceTrackerApp(QMainWindow):
    """Main application window for face tracking"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Tracker")
        self.setGeometry(100, 100, 800, 600)
        
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
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.face_count_label)
        
    def toggle_tracking(self):
        """Toggle face tracking on/off"""
        if not self.is_tracking:
            self.start_tracking()
        else:
            self.stop_tracking()
    
    def start_tracking(self):
        """Start face tracking"""
        self.tracker_thread = FaceTrackerThread()
        self.tracker_thread.frame_ready.connect(self.process_frame)
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
    
    def update_status(self):
        """Update status display"""
        if self.is_tracking and self.tracker_thread and self.tracker_thread.isRunning():
            self.status_label.setText("Status: Tracking Active - Camera Running")
        elif self.is_tracking:
            self.status_label.setText("Status: Tracking Active - Camera Starting...")
    
    def closeEvent(self, event):
        """Handle application close event"""
        self.stop_tracking()
        event.accept()

def main():
    """Main function to run the application"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = FaceTrackerApp()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 