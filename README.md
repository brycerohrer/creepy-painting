# Face Tracker Application

A Python application with a modern PyQt5 UI that tracks faces in real-time using OpenCV.

## Features

- **Real-time face detection** using OpenCV's Haar Cascade Classifier
- **Modern PyQt5 user interface** with styled buttons and status displays
- **Live video feed** from your webcam
- **Face tracking visualization** with green rectangles around detected faces
- **Face count display** showing the number of faces currently detected
- **Start/Stop controls** to easily toggle tracking on and off
- **Status indicators** showing the current tracking state

## Requirements

- Python 3.7 or higher
- Webcam/camera
- Windows, macOS, or Linux

## Installation

1. **Clone or download** this repository to your local machine

2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install opencv-python PyQt5 numpy
   ```

## Usage

1. **Run the application**:
   ```bash
   python face_tracker.py
   ```

2. **Click "Start Tracking"** to begin face detection
   - The application will access your webcam
   - Detected faces will be highlighted with green rectangles
   - The face count will update in real-time

3. **Click "Stop Tracking"** to stop the camera and face detection

4. **Close the application** when you're done

## How It Works

- **Face Detection**: Uses OpenCV's Haar Cascade Classifier to detect faces in each video frame
- **Real-time Processing**: Processes video frames at ~30 FPS for smooth tracking
- **Multi-threaded**: Face detection runs in a separate thread to keep the UI responsive
- **Visual Feedback**: Draws green rectangles around detected faces and displays count

## Troubleshooting

### Camera Access Issues
- Ensure your webcam is not being used by another application
- Check that your camera permissions are enabled
- Try running the application as administrator (Windows)

### Performance Issues
- Close other applications using the camera
- Ensure good lighting conditions for better face detection
- The application automatically adjusts frame processing to maintain performance

### Dependencies Issues
- Make sure you have the correct Python version
- Try updating pip: `pip install --upgrade pip`
- On some systems, you may need to install additional system packages for OpenCV

## Technical Details

- **Face Detection Algorithm**: Haar Cascade Classifier
- **Video Processing**: OpenCV (cv2)
- **User Interface**: PyQt5
- **Threading**: QThread for non-blocking face detection
- **Frame Rate**: ~30 FPS (adjustable via the `msleep(30)` parameter)

## Customization

You can modify the application by:
- Adjusting face detection parameters in the `detectMultiScale` function
- Changing the visual style by modifying the CSS-like stylesheets
- Adding additional detection features (eyes, smiles, etc.)
- Implementing face tracking persistence between frames

## License

This project is open source and available under the MIT License. 