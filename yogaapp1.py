import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import tensorflow as tf
import os
import webbrowser
import sys

# Import the create_lessons_tab function from the lessons module
from lessons import create_lessons_tab

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Define class names
CLASS_NAMES = [
   "Adho Mukha Svanasana",
"Adho Mukha Vrksasana",
"Alanasana",
"Anjaneyasana",
"Ardha Chandrasana",
"Ardha Matsyendrasana",
"Ardha Navasana",
"Ardha Pincha Mayurasana",
"Ashta Chandrasana",
"Baddha Konasana",
"Bakasana",
"Balasana",
"Bitilasana",
"Camatkarasana",
"Dhanurasana",
"Eka Pada Rajakapotasana",
"Garudasana",
"Halasana",
"Hanumanasana",
"Malasana",
"Marjaryasana",
"Navasana",
"Padmasana",
"Parsva Virabhadrasana",
"Parsvottanasana",
"Paschimottanasana",
"Phalakasana",
"Pincha Mayurasana",
"Salamba Bhujangasana",
"Salamba Sarvangasana",
"Setu Bandha Sarvangasana",
"Sivasana",
"Supta Kapotasana",
"Trikonasana",
"Upavistha Konasana",
"Urdhva Dhanurasana",
"Urdhva Mukha Svsnssana",
"Ustrasana",
"Utkatasana",
"Uttanasana",
"Utthita Hasta Padangusthasana",
"Utthita Parsvakonasana",
"Vasisthasana",
"Virabhadrasana One",
"Virabhadrasana Three",
"Virabhadrasana Two",
"Vrksasana"
]

# Initialize variables for lazy loading
model = None
mp_pose = None
pose = None
mp_drawing = None

def initialize_components():
    global model, mp_pose, pose, mp_drawing
    if model is None:
        print("Loading yoga pose model...")
      #  model_path = resource_path("yoga_pose_finetuned_model.keras")
        model_path = resource_path("yoga_pose_classifier.keras")

        model = tf.keras.models.load_model(model_path)
    
    if mp_pose is None:
        print("Initializing MediaPipe...")
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose()
        mp_drawing = mp.solutions.drawing_utils

# Initialize the main Tkinter window
root = tk.Tk()
root.title("Yoga Pose Analyzer")
root.geometry("950x720")

# Create a Notebook widget for tabbed navigation
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# -------- HOME TAB -------- #
home_tab = ttk.Frame(notebook)
notebook.add(home_tab, text="Home")

# Label to display the webcam feed
label = tk.Label(home_tab)
label.pack()

# Label to provide feedback on the predicted pose
feedback_label = tk.Label(
    home_tab, text="Press Start to begin", font=("Arial", 24), fg="blue"
)
feedback_label.pack()

# Variables to control the webcam feed
cap = None
running = False

def predict_pose(frame):
    global model
    if model is None:
        initialize_components()
    
    # Preprocess the frame
    img = cv2.resize(frame, (224, 224))
    img_array = np.expand_dims(img, axis=0)
    img_array = img_array / 255.0  # Normalize
    
    # Make prediction
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class]
    
    return CLASS_NAMES[predicted_class], confidence

def update_frame():
    global pose, mp_drawing
    if pose is None or mp_drawing is None:
        initialize_components()
    
    ret, frame = cap.read()
    if ret:
        # Convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe
        results = pose.process(rgb_frame)
        
        # Draw pose landmarks
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

        predicted_pose, confidence = predict_pose(frame)
        feedback_label.config(text=f"Predicted Pose: {predicted_pose} (Confidence: {confidence:.2f})")

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        label.imgtk = imgtk
        label.configure(image=imgtk)

    root.after(10, update_frame)

def start_camera():
    """
    Starts the webcam feed and begins processing frames.
    """
    global cap, running
    if not running:
        cap = cv2.VideoCapture(0)
        running = True
        update_frame()

def stop_camera():
    """
    Stops the webcam feed and resets the display.
    """
    global cap, running
    running = False
    if cap:
        cap.release()
        cap = None
    label.config(image="")
    feedback_label.config(text="Press Start to begin")

# Buttons to start and stop the webcam feed
start_button = tk.Button(
    home_tab,
    text="Start",
    command=start_camera,
    bg="green",
    fg="white",
    font=("Arial", 12),
)
start_button.pack(pady=5)

stop_button = tk.Button(
    home_tab,
    text="Stop",
    command=stop_camera,
    bg="red",
    fg="white",
    font=("Arial", 12),
)
stop_button.pack(pady=5)

# -------- SUPPORT TAB -------- #
support_tab = ttk.Frame(notebook)
notebook.add(support_tab, text="Support Us")

# Define the open_amazon function
def open_amazon():
    """
    Opens the default web browser to the specified Amazon link.
    """
    webbrowser.open("https://www.amazon.com")

# Create a main frame to hold content
support_content = ttk.Frame(support_tab)
support_content.pack(expand=True, pady=20)

# Title
title_label = tk.Label(
    support_content,
    text="Support Our Yoga App Development",
    font=("Arial", 18, "bold"),
    fg="#2E7D32"  # Dark green color
)
title_label.pack(pady=10)

# Description
description_label = tk.Label(
    support_content,
    text="Your support helps us improve and add new features!",
    font=("Arial", 12),
    wraplength=400
)
description_label.pack(pady=5)

# QR Code Image
try:
    qr_path = resource_path("data/qr_code.jpg")
    if not os.path.exists(qr_path):
        print("QR code image not found. Please add qr_code.jpg to the data directory.")
        qr_path = None
except Exception as e:
    print(f"Error loading QR code: {e}")
    qr_path = None

if qr_path:
    qr_image = Image.open(qr_path)
    qr_image = qr_image.resize((300, 300), Image.LANCZOS)  # Resize for better display
    qr_photo = ImageTk.PhotoImage(qr_image)
    qr_label = tk.Label(support_content, image=qr_photo)
    qr_label.image = qr_photo  # Keep a reference
    qr_label.pack(pady=15)
else:
    fallback_label = tk.Label(
        support_content,
        text="QR Code not available",
        font=("Arial", 14),
        fg="#666666"
    )
    fallback_label.pack(pady=15)

# Scan message
scan_label = tk.Label(
    support_content,
    text="Scan to Support Us!",
    font=("Arial", 14, "bold"),
    fg="#1976D2"  # Blue color
)
scan_label.pack(pady=5)

# Alternative support method
alternative_frame = ttk.Frame(support_content)
alternative_frame.pack(pady=20)

tk.Label(
    alternative_frame,
    text="Or support us through Amazon:",
    font=("Arial", 12)
).pack(side=tk.LEFT, padx=5)

tk.Button(
    alternative_frame,
    text="Shop on Amazon",
    command=open_amazon,
    bg="#FF9900",  # Amazon orange
    fg="white",
    font=("Arial", 12),
    cursor="hand2"
).pack(side=tk.LEFT, padx=5)

# -------- LESSONS TAB -------- #
# Ensure the notebook is passed to the create_lessons_tab function
lessons_tab = create_lessons_tab(notebook)
notebook.add(lessons_tab, text="Lessons")

# Start the Tkinter main event loop
root.mainloop()
