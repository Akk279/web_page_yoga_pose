# YogaAnalyzer

A desktop application that uses computer vision and machine learning to analyze and provide feedback on yoga poses in real-time.

## Features

- Real-time yoga pose analysis using MediaPipe and TensorFlow
- Voice feedback for pose corrections
- Interactive lessons with pose demonstrations
- QR code integration for additional resources
- User-friendly interface with camera feed display

## Technology Stack

### Core Technologies
- **Python 3.12+**: Primary programming language
- **Tkinter**: Native GUI framework for desktop interface
- **TensorFlow**: Machine learning framework for pose classification
- **MediaPipe**: Real-time pose detection and tracking
- **OpenCV**: Computer vision and camera processing
- **PyTTSx3**: Text-to-speech engine for voice feedback

### Development Tools
- **PyInstaller**: Application packaging and distribution
- **PIL (Python Imaging Library)**: Image processing and manipulation
- **NumPy**: Numerical computing and array operations
- **JSON**: Data serialization for pose information
- **Threading**: Concurrent processing for real-time analysis
- **Queue**: Inter-thread communication
- **Webbrowser**: External resource integration

### System Requirements

#### Hardware Requirements
- **Processor**: Intel Core i5 or equivalent (2.5 GHz or higher)
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 2GB available space
- **Camera**: Webcam with 720p resolution or higher
- **Audio**: Working speakers or headphones
- **Display**: 1366x768 resolution minimum

#### Software Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Python 3.12+**: Latest stable version
- **CUDA Support**: Optional for GPU acceleration
- **Audio Drivers**: Latest version for voice feedback
- **Camera Drivers**: Latest version for optimal performance

#### Network Requirements
- **Internet Connection**: Required for initial setup and updates
- **Bandwidth**: 5 Mbps minimum for smooth operation
- **Latency**: <100ms for real-time feedback

### Development Environment Setup

1. **Python Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **GPU Setup (Optional)**
   ```bash
   # Install CUDA Toolkit
   # Install cuDNN
   pip install tensorflow-gpu
   ```

3. **Development Tools**
   ```bash
   # Install development dependencies
   pip install black pylint pytest
   ```

### Performance Considerations

1. **CPU Optimization**
   - Multi-threading for parallel processing
   - Frame rate optimization (30 FPS target)
   - Memory management for large models

2. **GPU Acceleration**
   - TensorFlow GPU support
   - CUDA optimization
   - Batch processing capabilities

3. **Memory Management**
   - Efficient resource loading
   - Cache management
   - Garbage collection optimization

4. **Real-time Processing**
   - Frame buffering
   - Pose detection optimization
   - Feedback latency minimization

## Application Architecture

### Frontend Implementation
The frontend was developed using Tkinter, Python's native GUI toolkit, chosen for its lightweight nature and seamless integration with Python's data processing capabilities. The user interface features a tabbed design with three main sections: a welcoming home screen with application overview, an interactive session interface with real-time camera feed and pose visualization overlays, and an informative about section. The interface design emphasizes simplicity and focus, using clean layouts and intuitive controls that align with the meditative essence of yoga practice. Custom UI components were developed to handle camera feed display, pose selection, and real-time feedback presentation.

### Backend Implementation
The backend was implemented using Python's robust ecosystem of scientific computing libraries. TensorFlow serves as the core engine for pose classification, while MediaPipe provides real-time pose detection and landmark tracking. The system architecture follows a modular design, with separate components handling camera input processing, pose analysis, and feedback generation. Local file system storage is utilized for model persistence, resource management, and session data, ensuring quick access and reliable performance. The application maintains a stateful design that manages user sessions, pose analysis metrics, and feedback generation through in-memory processing and local storage.

### Data Processing Pipeline
1. **Input Processing**
   - Real-time camera feed capture using OpenCV
   - Frame preprocessing and optimization
   - Pose landmark detection via MediaPipe

2. **Analysis Engine**
   - Keypoint extraction and normalization
   - Pose classification using TensorFlow model
   - Confidence scoring and validation

3. **Feedback Generation**
   - Real-time pose comparison
   - Dynamic feedback selection
   - Voice instruction synthesis

### Integration Architecture
The application follows a tightly-coupled integration model where:
- Camera input is directly processed by the pose detection module
- Analysis results are immediately available to the feedback system
- UI updates are synchronized with the analysis pipeline
- Voice feedback is generated in real-time based on pose analysis

This architecture ensures minimal latency and maximum responsiveness, crucial for real-time yoga pose analysis and feedback.

## Voice Guidance Module

The Voice Guidance Module delivers intelligent, real-time instructions using natural language voice prompts. This module bridges the sensory gap for users who may not be actively looking at the screen during practice. It uses pre-generated scripts aligned with each yoga pose and dynamically delivers them based on pose recognition status.

### Core Components

1. **Text-to-Speech Engine**
   ```python
   # Initialization with customizable properties
   tts_engine = pyttsx3.init()
   tts_engine.setProperty('rate', 150)    # Adjustable speech speed
   tts_engine.setProperty('volume', 0.9)  # Configurable volume
   tts_engine.setProperty('voice', 'en-US')  # Language selection
   ```

2. **Speech Management System**
   ```python
   # Speech timing and cooldown
   last_speech_time = 0
   SPEECH_COOLDOWN = 4  # Minimum seconds between voice feedback
   
   # Voice templates
   VOICE_TEMPLATES = {
       'motivational': ["Great job!", "You're doing well!", "Keep it up!"],
       'corrective': ["Please adjust your", "Try to", "Remember to"],
       'breathing': ["Inhale deeply", "Hold the breath", "Exhale slowly"]
   }
   ```

### Key Features

1. **Context-Aware Feedback**
   - Dynamic response based on pose confidence scores
   - Intelligent selection of feedback type (praise, correction, guidance)
   - Real-time adjustment of instruction complexity

2. **Natural Language Processing**
   - Custom phrase generation based on pose analysis
   - Contextual understanding of user's current state
   - Adaptive feedback based on session progress

3. **Multilingual Support**
   - Multiple language options for voice prompts
   - Region-specific terminology for yoga poses
   - Cultural adaptation of instructions

4. **Breathing Integration**
   - Synchronized breathing cues with pose transitions
   - Calm, meditative tone for relaxation phases
   - Progressive breathing guidance

### Implementation Details

1. **Voice Template System**
   ```python
   def get_voice_template(context, confidence):
       if confidence > 0.8:
           return random.choice(VOICE_TEMPLATES['motivational'])
       elif confidence > 0.5:
           return random.choice(VOICE_TEMPLATES['corrective'])
       else:
           return "Please adjust your pose"
   ```

2. **Dynamic Feedback Generation**
   ```python
   def generate_feedback(predicted_pose, confidence, target_pose):
       if predicted_pose == target_pose:
           return f"Excellent! You're holding {target_pose} correctly"
       else:
           return f"Try to adjust towards {target_pose}"
   ```

3. **Breathing Coordination**
   ```python
   def provide_breathing_guidance(pose_stage):
       if pose_stage == 'transition':
           return "Inhale deeply as you move"
       elif pose_stage == 'hold':
           return "Hold the pose and breathe steadily"
   ```

### Feedback Categories

1. **Motivational Feedback**
   - "Excellent form! You're mastering this pose"
   - "Your balance is improving"
   - "Great focus and control"

2. **Corrective Guidance**
   - "Please straighten your back"
   - "Try to align your shoulders"
   - "Maintain steady breathing"

3. **Breathing Instructions**
   - "Inhale deeply through your nose"
   - "Hold the breath for three counts"
   - "Exhale slowly and relax"

4. **Transition Cues**
   - "Prepare to move into the next pose"
   - "Shift your weight gradually"
   - "Maintain control during the transition"

### Advanced Features

1. **Personalization**
   - User preference for voice tone (formal/friendly/meditative)
   - Adjustable feedback frequency
   - Customizable instruction complexity

2. **Session Analytics**
   - Tracking of common correction areas
   - Progress-based feedback adjustment
   - Personalized improvement suggestions

3. **Error Handling**
   ```python
   try:
       tts_engine.say(text)
       tts_engine.runAndWait()
   except Exception as e:
       print(f"Voice feedback error: {e}")
       # Fallback to visual feedback
   ```

### Usage Guidelines

1. **System Requirements**
   - Working audio output
   - PyTTSx3 library
   - System text-to-speech engine
   - Sufficient system resources for voice processing

2. **Best Practices**
   - Clear, concise instructions
   - Appropriate feedback timing
   - Balanced mix of correction and encouragement
   - Cultural sensitivity in language use

3. **Troubleshooting**
   - Audio output verification
   - Voice engine configuration
   - Resource monitoring
   - Fallback mechanisms

## Project Structure

```
.
├── yogaapp1.py              # Main application file
├── lessons.py               # Yoga lessons and pose analysis module
├── yoga_pose_finetuned_model.keras  # Trained model for pose classification
├── data/                    # Resource files
│   ├── asanas/             # Yoga pose images and data
│   └── qr_code.jpg         # QR code for additional resources
├── app_icon.ico            # Application icon
└── requirements.txt        # Python dependencies
```

## Installation

1. Install Python 3.12 or later
2. Install required dependencies:
   ```bash
    pip install -r requirements.txt
    ```

## Web Application (FastAPI)

### Quick start

1. Install deps (ideally in a venv):
   ```bash
   pip install -r requirements.txt
   ```
2. Install web-only deps and start the API in its own folder:
   ```bash
   cd webapp
   python -m pip install -r requirements.txt
   python main.py
   ```
   - Health check: `http://127.0.0.1:8000/health`
   - Predict endpoint: `POST /predict` with form field `file` (image)
3. Open the simple web UI:
   - Open `webapp/static/index.html` in your browser
   - Ensure the API Base field is `http://127.0.0.1:8000`
   - Click "Start Camera" then "Predict Frame"

Notes:
- The API loads `yoga_pose_finetuned_model.keras` from the project root.
- CORS is enabled for local development by default.

## Building the Executable

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller yogaapp1.spec
   ```

The executable will be created in the `dist` directory.

## Code Documentation

### Main Application (yogaapp1.py)

#### Key Components

1. **Resource Management**
   - `resource_path(relative_path)`: Handles resource file paths for both development and packaged environments

2. **UI Components**
   - `create_home_tab()`: Creates the home tab with welcome message and QR code
   - `create_lessons_tab()`: Creates the lessons tab with pose selection and camera feed
   - `create_about_tab()`: Creates the about tab with application information

3. **Camera Management**
   - `start_camera()`: Initializes and starts the camera feed
   - `stop_camera()`: Stops the camera and releases resources
   - `update_frame()`: Updates the camera feed with pose analysis

4. **Pose Analysis**
   - `predict_pose(frame)`: Analyzes the current pose and provides feedback
   - `speak_feedback(text)`: Provides voice feedback for pose corrections

### Lessons Module (lessons.py)

#### Key Components

1. **Model Management**
   - `initialize_model()`: Loads the trained pose classification model
   - `predict_pose(frame)`: Analyzes the current pose and returns predictions

2. **Pose Data**
   - `load_asana_data()`: Loads yoga pose information and instructions
   - `asanas`: Dictionary containing pose names and descriptions

3. **UI Components**
   - `create_lessons_tab()`: Creates the interactive lessons interface
   - `update_pose_info()`: Updates the display with current pose information

4. **Camera and Analysis**
   - `start_camera()`: Initializes camera for pose analysis
   - `stop_camera()`: Stops camera and releases resources
   - `update_frame()`: Processes camera feed and provides real-time feedback

## Usage

1. Launch the application
2. Select the "Lessons" tab
3. Choose a yoga pose from the dropdown menu
4. Position yourself in view of the camera
5. Follow the on-screen instructions and voice feedback to improve your pose

## Dependencies

- Python 3.12+
- TensorFlow
- MediaPipe
- OpenCV
- PyTTSx3
- Tkinter
- NumPy
- PIL (Python Imaging Library)

## Notes

- The application requires a webcam for pose analysis
- Ensure proper lighting for accurate pose detection
- The first run might take longer as the model initializes
- Voice feedback can be toggled on/off in the interface

## Troubleshooting

1. **Camera not working**
   - Ensure the camera is properly connected
   - Check if another application is using the camera
   - Verify camera permissions

2. **Model not loading**
   - Check if `yoga_pose_finetuned_model.keras` is in the correct location
   - Verify TensorFlow installation

3. **Voice feedback not working**
   - Check system audio settings
   - Verify PyTTSx3 installation

## License

This project is licensed under the MIT License - see the LICENSE file for details.
