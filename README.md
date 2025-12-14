# Yoga Pose Analyzer Web Application

A FastAPI-based web application that uses machine learning to analyze and provide feedback on yoga poses in real-time.

## Features

- Real-time yoga pose analysis using TensorFlow
- Interactive web interface with camera feed
- User authentication and gamification
- Yoga lessons and pose demonstrations
- RESTful API for pose prediction

## Technology Stack

- **FastAPI**: Modern web framework for building APIs
- **TensorFlow**: Machine learning framework for pose classification
- **Uvicorn**: ASGI server for running the application
- **Pillow**: Image processing
- **NumPy**: Numerical computing

## Installation

1. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   cd webapp
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the FastAPI server:**
   ```bash
   cd webapp
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn webapp.main:app --reload
   ```

2. **Access the application:**
   - API: http://127.0.0.1:8000
   - Health check: http://127.0.0.1:8000/health
   - Web interface: http://127.0.0.1:8000/static/index.html

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /predict` - Predict yoga pose from uploaded image
- `GET /static/*` - Serve static HTML files
- `GET /assets/*` - Serve yoga pose data and images

## Project Structure

```
.
├── webapp/              # Main application directory
│   ├── main.py         # FastAPI application entry point
│   ├── lessons_api.py  # Lessons API router
│   ├── auth/           # Authentication module
│   ├── gamification/   # Gamification features
│   └── static/         # Frontend HTML/JS files
├── data/               # Yoga pose data and images
│   └── asanas/         # Individual pose data
├── yoga_pose_finetuned_model.keras  # Trained ML model
└── categories.json     # Pose categories

```

## Usage

1. Open the web interface in your browser
2. Click "Start Camera" to enable webcam access
3. Position yourself in view of the camera
4. Click "Predict Frame" to analyze your current pose
5. View the predicted pose and confidence score

## Requirements

- Python 3.12+
- Webcam for pose analysis
- Modern web browser with camera access

## License

This project is licensed under the MIT License.
