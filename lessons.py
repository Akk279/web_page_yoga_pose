#lessons
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import urllib.request
import io
import cv2
import tensorflow as tf
import numpy as np
import threading
import queue
import time
import os
import traceback
import json
import webbrowser # For opening YouTube links
import pyttsx3
import mediapipe as mp
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Initialize variables for lazy loading
model = None

def initialize_model():
    global model
    if model is None:
        print("Loading yoga pose model...")
        model_path = resource_path("yoga_pose_finetuned_model.keras")
        model = tf.keras.models.load_model(model_path)

def predict_pose(frame):
    global model
    if model is None:
        initialize_model()
    
    # Preprocess the frame
    img = cv2.resize(frame, (224, 224))
    img_array = np.expand_dims(img, axis=0)
    img_array = img_array / 255.0  # Normalize
    
    # Make prediction
    predictions = model.predict(img_array, verbose=0)
    predicted_class = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class]
    
    return predicted_class, confidence

# Try to load the model upfront
try:
    print("Loading yoga pose model...")
    MODEL_PATH = "yoga_pose_finetuned_model.keras"
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        print("Model loaded successfully!")
        
        # Get class names directly from file structure
        train_dir = "F:/vs studio code/yoga/YOGA_NEW_DATASET/train"
        if os.path.exists(train_dir):
            CLASS_NAMES = sorted([d for d in os.listdir(train_dir) 
                             if os.path.isdir(os.path.join(train_dir, d))])
            
            # Remove 'neutral' class if present
            if "neutral" in CLASS_NAMES:
                CLASS_NAMES.remove("neutral")
                
            NUM_CLASSES = len(CLASS_NAMES)
            print(f"Class names loaded: {NUM_CLASSES} classes - {CLASS_NAMES}")
        else:
            print(f"Training directory not found: {train_dir}")
            CLASS_NAMES = []
            NUM_CLASSES = 0
    else:
        print(f"Model file not found: {MODEL_PATH}")
        model = None
        CLASS_NAMES = []
        NUM_CLASSES = 0
        
except Exception as e:
    print(f"Error loading model: {e}")
    traceback.print_exc()
    model = None
    CLASS_NAMES = []
    NUM_CLASSES = 0

# --- Global variables for camera state ---
cap = None
camera_active = False
current_pose_target = None
camera_label = None # This will be assigned the ttk.Label widget

# Add a global prediction queue for thread communication
pred_queue = queue.Queue(maxsize=1)  # Only need the latest prediction

# Initialize text-to-speech engine
try:
    tts_engine = pyttsx3.init()
    # Set properties (optional)
    tts_engine.setProperty('rate', 150)    # Speed of speech
    tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
except Exception as e:
    print(f"Error initializing text-to-speech: {e}")
    tts_engine = None

# Add a function to speak text in a non-blocking way
def speak_feedback(text):
    global last_speech_time
    current_time = time.time()
    
    # Check if enough time has passed since last speech
    if current_time - last_speech_time < SPEECH_COOLDOWN:
        return
        
    if tts_engine is not None:
        try:
            # Run speech in a separate thread to avoid blocking the UI
            threading.Thread(target=tts_engine.say, args=(text,), daemon=True).start()
            threading.Thread(target=tts_engine.runAndWait, daemon=True).start()
            last_speech_time = current_time
        except Exception as e:
            print(f"Error in speech feedback: {e}")

# --- Helper function to load data from folders ---
def load_asana_data():
    asana_data = {}
    # Define the base path relative to the script location or use absolute path
    base_dir = os.path.dirname(os.path.abspath(__file__)) # Gets directory of lessons.py
    asanas_dir = os.path.join(base_dir, "data", "asanas") # Path: yoga/data/asanas
    print(f"--- DEBUG: Looking for asana data in: {asanas_dir} ---")

    if not os.path.isdir(asanas_dir):
        print(f"--- WARNING: Asana data directory not found: {asanas_dir} ---")
        print("Please create the folder structure: yoga/data/asanas/[asana_name]/info.json")
        return {} # Return empty if base directory doesn't exist

    # Iterate through each folder inside 'asanas' directory
    for asana_folder_name in os.listdir(asanas_dir):
        asana_path = os.path.join(asanas_dir, asana_folder_name)
        if os.path.isdir(asana_path):
            info_file_path = os.path.join(asana_path, "info.json")
            image_dir_path = os.path.join(asana_path, "images")
            asana_info = {}
            display_name = asana_folder_name # Default display name

            # Load info.json if it exists
            if os.path.isfile(info_file_path):
                try:
                    with open(info_file_path, 'r', encoding='utf-8') as f:
                        asana_info = json.load(f)
                    # Create a more user-friendly display name if possible
                    sanskrit_name = asana_info.get("name", asana_folder_name)
                    english_name = asana_info.get("english_name", "")
                    if english_name:
                        display_name = f"{sanskrit_name} ({english_name})"
                    else:
                        display_name = sanskrit_name
                    print(f"--- DEBUG: Loaded info for '{display_name}'")

                    # --- ADD THIS CHECK ---
                    if not display_name:
                        print(f"--- WARNING: Skipping asana in folder '{asana_folder_name}' due to empty generated display name (check 'name' field in info.json). ---")
                        continue # Skip to the next folder in the loop
                    # --- END OF CHECK ---

                except Exception as e:
                    print(f"--- ERROR loading {info_file_path}: {e} ---")
            else:
                 print(f"--- WARNING: info.json not found for {asana_folder_name} ---")

            # Store the loaded info and paths using the display_name as the key
            # This part only runs if display_name was not empty
            asana_data[display_name] = {
                "folder_name": asana_folder_name,
                "info": asana_info,
                "image_dir": image_dir_path if os.path.isdir(image_dir_path) else None
            }
        else:
             print(f"--- DEBUG: Skipping non-directory item: {asana_folder_name} ---")


    print(f"--- DEBUG: Loaded data for {len(asana_data)} asanas. ---")
    return asana_data

# --- Helper function to open URLs ---
def open_url(url):
    print(f"--- DEBUG: Opening URL: {url} ---")
    try:
        webbrowser.open(url, new=2) # Open in new tab/window
    except Exception as e:
        print(f"--- ERROR opening URL {url}: {e} ---")

# --- Main Function to Create the Tab ---
def create_lessons_tab(notebook):
    global camera_label
    
    # Create the tab
    tab = ttk.Frame(notebook)
    
    # Track tab visibility - initialize to True since tab is visible when created
    tab_is_visible = True
    
    # Function to handle tab visibility changes
    def on_tab_change(event):
        nonlocal tab_is_visible  # Use nonlocal since it's defined in create_lessons_tab
        global camera_active, cap
        
        try:
            # Get the currently selected tab
            current_tab = notebook.select()
            
            # Check if our tab is the current one
            if current_tab == str(tab):
                print("Lessons tab is now visible")
                tab_is_visible = True
                
                # If camera was active but released, restart it
                if camera_active and (cap is None or not cap.isOpened()):
                    print("Restarting camera after tab change")
                    # Use a delay to let UI fully update
                    tab.after(200, lambda: start_camera_feed(camera_status))
            else:
                print("Lessons tab is now hidden")
                tab_is_visible = False
                
                # Release camera when tab not visible to save resources
                if camera_active and cap is not None:
                    print("Pausing camera while tab not visible")
                    cap.release()
                    cap = None
        except Exception as e:
            print(f"Error in tab change handler: {e}")
    
    # Bind tab change event
    notebook.bind("<<NotebookTabChanged>>", on_tab_change)
    
    # Function to safely stop camera
    def safe_camera_stop():
        global camera_active, cap
        print("Tab being destroyed, ensuring camera stops")
        camera_active = False  # Stop the update loop
        try:
            if cap is not None:
                cap.release()
                cap = None
        except Exception as e:
            print(f"Error stopping camera: {e}")
    
    # Bind destroy event
    tab.bind("<Destroy>", lambda e: safe_camera_stop() if e.widget == tab else None)
    
    # Load asana data
    asana_data = load_asana_data()
    print("--- DEBUG: Loaded asana_data keys:", sorted(list(asana_data.keys())))

    # Main PanedWindow
    paned_window = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)

    # --- Left Frame: Scrollable Pose List ---
    list_frame = ttk.Frame(paned_window, width=300)
    paned_window.add(list_frame, weight=1)

    canvas = tk.Canvas(list_frame)
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas) # Holds the lesson sections

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    # -----------------------------------------

    # --- Right Frame: Scrollable Pose Details ---
    detail_frame = ttk.Frame(paned_window)
    paned_window.add(detail_frame, weight=3)
    
    # Create canvas and scrollbar for the right side
    detail_canvas = tk.Canvas(detail_frame)
    detail_scrollbar = ttk.Scrollbar(detail_frame, orient="vertical", command=detail_canvas.yview)
    
    # Create a frame to hold all the content that will be scrolled
    detail_content_frame = ttk.Frame(detail_canvas)
    
    # Configure the canvas
    detail_canvas.configure(yscrollcommand=detail_scrollbar.set)
    
    # Pack scrollbar and canvas
    detail_scrollbar.pack(side="right", fill="y")
    detail_canvas.pack(side="left", fill="both", expand=True)
    
    # Create window in canvas and bind it to the frame
    detail_canvas.create_window((0, 0), window=detail_content_frame, anchor="nw", tags="detail_content")
    
    # Configure canvas scrolling
    def configure_detail_scroll(event):
        detail_canvas.configure(scrollregion=detail_canvas.bbox("all"))
        # Set the width of the window to match the canvas width
        detail_canvas.itemconfig("detail_content", width=event.width)
    
    detail_content_frame.bind("<Configure>", configure_detail_scroll)
    detail_canvas.bind("<Configure>", lambda e: detail_canvas.itemconfig("detail_content", width=e.width))
    
    # Enable mouse wheel scrolling
    def on_detail_mousewheel(event):
        detail_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    detail_canvas.bind_all("<MouseWheel>", on_detail_mousewheel)
    
    # When the tab is destroyed, remove the mousewheel binding
    def on_detail_destroy(event):
        detail_canvas.unbind_all("<MouseWheel>")
    
    detail_frame.bind("<Destroy>", on_detail_destroy)

    # Add all content to detail_content_frame instead of detail_frame
    detail_title = ttk.Label(detail_content_frame, text="Select a Pose", font=("Arial", 16, "bold"))
    detail_title.pack(pady=10)

    desc_label = ttk.Label(detail_content_frame, text="Description:")
    desc_label.pack(anchor="w", padx=10)
    desc_text = scrolledtext.ScrolledText(detail_content_frame, height=5, wrap=tk.WORD, state=tk.DISABLED)
    desc_text.pack(fill="x", padx=10, pady=5)

    img_label_detail = ttk.Label(detail_content_frame, text="Image Area")
    img_label_detail.pack(pady=10)

    yt_link_label = ttk.Label(detail_content_frame, text="YouTube Link: N/A", foreground="blue", cursor="hand2")
    yt_link_label.pack(pady=5)

    # Camera frame
    camera_prediction_frame = ttk.Frame(detail_content_frame)
    camera_prediction_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Camera container with fixed size
    camera_container = ttk.Frame(camera_prediction_frame, width=640, height=480)
    camera_container.pack(padx=10, pady=10)
    camera_container.pack_propagate(False)

    # Camera label
    camera_label = ttk.Label(camera_container, background="black")
    camera_label.pack(fill=tk.BOTH, expand=True)
    
    # Camera control section
    control_frame = ttk.Frame(camera_prediction_frame)
    control_frame.pack(fill="x", padx=10, pady=5)
    
    # Camera status
    camera_status = ttk.Label(control_frame, text="Camera: Not started")
    camera_status.pack(side=tk.LEFT, padx=5)
    
    # Camera buttons
    start_btn = ttk.Button(control_frame, text="Start Camera", 
                          command=lambda: start_camera_feed(camera_status))
    start_btn.pack(side=tk.LEFT, padx=5)
    
    stop_btn = ttk.Button(control_frame, text="Stop Camera", 
                        command=lambda: stop_camera_feed(camera_status))
    stop_btn.pack(side=tk.LEFT, padx=5)

    restart_btn = ttk.Button(control_frame, text="Restart Camera", 
                          command=lambda: restart_camera(camera_status))
    restart_btn.pack(side=tk.LEFT, padx=5)

    # Camera size toggle
    def toggle_camera_size():
        current_width = camera_container.winfo_width()
        if current_width == 640:  # Normal size
            camera_container.configure(width=960, height=720)  # 1.5x larger
            camera_size_btn.configure(text="Shrink Camera")
        else:  # Expanded size
            camera_container.configure(width=640, height=480)  # Original size
            camera_size_btn.configure(text="Expand Camera")
        
        # Force container to update its size
        camera_container.pack_propagate(False)
        # Update the scroll region after size change
        detail_canvas.configure(scrollregion=detail_canvas.bbox("all"))

    camera_size_btn = ttk.Button(control_frame, text="Expand Camera", 
                                command=toggle_camera_size)
    camera_size_btn.pack(side=tk.LEFT, padx=5)

    # Feedback frame
    feedback_frame = ttk.LabelFrame(camera_prediction_frame, text="Pose Analysis")
    feedback_frame.pack(fill=tk.X, padx=10, pady=10)

    detected_pose_label = ttk.Label(feedback_frame, text="Select a pose to begin analysis",
                                   font=("Arial", 11))
    detected_pose_label.pack(anchor='w', padx=10, pady=5)

    feedback_result_label = ttk.Label(feedback_frame, text="Waiting for camera...",
                                   font=("Arial", 11, "bold"), foreground="blue")
    feedback_result_label.pack(anchor='w', padx=10, pady=5)

    # --- Define Helper Functions ---

    def get_image_from_web(query):
        # Indented block for the function
        try:
            search_term = query.split('(')[0].strip()
            url = f"https://source.unsplash.com/random/300x225/?yoga,{search_term.replace(' ', '-')}"
            print(f"Fetching image from: {url}")
            with urllib.request.urlopen(url, timeout=10) as u:
                raw_data = u.read()
            im = Image.open(io.BytesIO(raw_data))
            # Optional resize:
            # im = im.resize((300, 225), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(im)
        except Exception as e:
            print(f"Error fetching image for {query}: {e}")
            return None

    def start_camera_feed(status_label):
        nonlocal tab_is_visible
        global cap, camera_active, camera_label
        
        # Don't start if tab isn't visible
        if not tab_is_visible:
            print("Not starting camera - tab not visible")
            return
        
        if camera_active and cap is not None and cap.isOpened():
            print("Camera already running")
            return
        
        # Set active flag even if video capture fails (will try to restart later)
        camera_active = True
        
        print("Starting camera...")
        try:
            # Initialize camera
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("Failed with default method, trying with CAP_DSHOW")
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                
                if not cap.isOpened():
                    print("ERROR: Could not open camera")
                    update_status(status_label, "Camera: Error - Cannot open camera")
                    return False
            
            # Camera opened successfully
            update_status(status_label, "Camera: Running")
            
            # Print properties
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            print(f"Camera opened: {width}x{height} at {fps} FPS")
            
            # Start the update loop
            tab.after(50, lambda: update_camera_feed(tab, status_label))
            return True
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            update_status(status_label, f"Camera: Error - {str(e)[:20]}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_camera_feed(widget, status_label):
        global cap, camera_active, camera_label, current_pose_target, model, CLASS_NAMES
        
        if not camera_active or not camera_label or not camera_label.winfo_exists():
            stop_camera_feed(None)
            return
        
        try:
            ret, frame = cap.read()
            if not ret:
                status_label and status_label.winfo_exists() and status_label.config(text="Camera: Error - No frame")
                stop_camera_feed(status_label)
                return
                
            # Process frame once for both display and prediction
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Only do prediction if all requirements are met
            if all([model, CLASS_NAMES, current_pose_target]):
                try:
                    # Reuse resized frame for prediction
                    resized_frame = cv2.resize(frame_rgb, (224, 224))
                    img_array = np.expand_dims(resized_frame, axis=0).astype("float32") / 255.0
                    
                    predictions = model.predict(img_array, verbose=0)
                    confidence = np.max(predictions)
                    
                    if confidence > 0.50:
                        predicted_class_index = np.argmax(predictions)
                        if predicted_class_index < len(CLASS_NAMES):
                            update_pose_feedback(CLASS_NAMES[predicted_class_index], confidence)
                    else:
                        update_pose_feedback(None, confidence)
                except Exception as pred_error:
                    print(f"Error during pose prediction: {pred_error}")
                    detected_pose_label.config(text="Error in pose detection")
            
            # Update camera display
            update_camera_display(frame_rgb)
            
            # Schedule next update if active
            if camera_active and widget and widget.winfo_exists():
                widget.after(50, lambda: update_camera_feed(widget, status_label))
                
        except Exception as e:
            print(f"Error in camera feed: {e}")
            if camera_active and widget and widget.winfo_exists():
                widget.after(1000, lambda: update_camera_feed(widget, status_label))
            else:
                stop_camera_feed(None)

    def update_pose_feedback(predicted_pose, confidence):
        """Helper function to update pose feedback"""
        if not predicted_pose:
            detected_pose_label.config(text=f"No clear pose detected ({confidence:.0%})")
            feedback_result_label.config(
                text="⚠️ Please try to get fully in frame",
                foreground="blue"
            )
            speak_feedback("Please make sure you are fully visible in the camera")
            return
            
        detected_pose_label.config(text=f"Detected: {predicted_pose} ({confidence:.0%})")
        
        target_base_name = current_pose_target.split('(')[0].strip().lower()
        predicted_base_name = predicted_pose.lower()
        
        if predicted_base_name in target_base_name or target_base_name in predicted_base_name:
            feedback_result_label.config(
                text="✅ Great job! Correct pose detected!",
                foreground="green"
            )
            speak_feedback("Excellent! You're doing the pose correctly!")
        elif confidence > 0.70:
            feedback_result_label.config(
                text=f"❌ That's {predicted_pose}, not {current_pose_target.split('(')[0]}!",
                foreground="red"
            )
            speak_feedback("Please adjust your pose to match the target pose")
        else:
            feedback_result_label.config(
                text="⚠️ Try to match the selected pose better",
                foreground="orange"
            )
            speak_feedback("Keep trying, adjust your position")

    def update_camera_display(frame_rgb):
        """Helper function to update camera display"""
        container_width = camera_container.winfo_width()
        container_height = camera_container.winfo_height()
        
        if container_width > 20 and container_height > 20:
            pil_img = Image.fromarray(frame_rgb).resize((container_width, container_height), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(image=pil_img)
            
            if camera_label.winfo_exists():
                camera_label.config(image=tk_img)
                camera_label.image = tk_img

    def stop_camera_feed(status_label=None):
        global cap, camera_active, camera_label
        
        print("Stopping camera")
        camera_active = False
        
        if cap is not None:
            cap.release()
            cap = None
        
        # Check if camera_label still exists before configuring it
        try:
            if camera_label and camera_label.winfo_exists():
                camera_label.config(image="")
                camera_label.image = None  # Clear reference
        except Exception as e:
            print(f"Error clearing camera label: {e}")
        
        # Check if status_label still exists
        try:
            if status_label and status_label.winfo_exists():
                status_label.config(text="Camera: Stopped")
        except Exception as e:
            print(f"Error updating status label: {e}")
    
    def update_status(label, message):
        try:
            if label and label.winfo_exists():
                label.config(text=message)
        except Exception as e:
            print(f"Error updating status: {e}")

    def restart_camera(status_label):
        # Force a complete camera reset
        global camera_active, cap
        
        # Stop completely
        camera_active = False
        if cap is not None:
            cap.release()
            cap = None
        
        # Clear the display
        try:
            if camera_label and camera_label.winfo_exists():
                camera_label.config(image="")
                camera_label.image = None
        except Exception as e:
            print(f"Error clearing camera display: {e}")
        
        # Short delay then restart
        tab.after(500, lambda: start_camera_feed(status_label))

    def display_pose_details(pose_name):
        # Use nonlocal for widgets/vars defined in create_lessons_tab that need modification
        nonlocal detail_title, desc_text, img_label_detail, yt_link_label, detected_pose_label, feedback_result_label
        # Use globals for camera state vars
        global current_pose_target, camera_active, cap

        print(f"--- DEBUG: display_pose_details called for: {pose_name} ---")
        
        # Update the target pose and set clear feedback message
        current_pose_target = pose_name
        detected_pose_label.config(text=f"Target pose: {pose_name}")
        feedback_result_label.config(text="Analyzing your pose...", foreground="blue")
        
        # --- Fetch data from the loaded dictionary ---
        pose_data = asana_data.get(pose_name) # Get the dictionary for this pose
        if not pose_data:
            print(f"--- WARNING: No local data found for pose: {pose_name} ---")
            # Optionally display an error message or default content
            detail_title.config(text=f"{pose_name} (Data not found)")
            desc_text.config(state=tk.NORMAL)
            desc_text.delete('1.0', tk.END)
            desc_text.insert(tk.END, "Detailed information for this pose could not be loaded from the local data folder.")
            desc_text.config(state=tk.DISABLED)
            img_label_detail.config(image="", text="Data not found")
            img_label_detail.image = None
            yt_link_label.config(text="Link N/A", foreground="grey", cursor="")
            # Optionally stop camera or prevent start if data is missing
            # stop_camera_feed()
            return # Exit the function if no data

        asana_info = pose_data.get("info", {})
        image_dir = pose_data.get("image_dir")
        # --- End of data fetching ---

        try:
            detail_title.config(text=pose_name) # Set title anyway

            # --- Update Description ---
            description = asana_info.get("description", "No description available.")
            benefits = asana_info.get("benefits", [])
            if benefits and benefits != [""]: # Check if benefits list has actual content
                description += "\n\nBenefits:\n" + "\n".join([f"• {b}" for b in benefits if b]) # Filter empty strings

            desc_text.config(state=tk.NORMAL)
            desc_text.delete('1.0', tk.END)
            desc_text.insert(tk.END, description)
            desc_text.config(state=tk.DISABLED)

            # --- Load Local Image ---
            photo = None
            if image_dir: # Check if image_dir path exists
                try:
                    image_files = [f for f in os.listdir(image_dir)
                                  if os.path.isfile(os.path.join(image_dir, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
                    if image_files:
                        image_path = os.path.join(image_dir, image_files[0]) # Load the first image
                        print(f"--- DEBUG: Loading local image: {image_path} ---")
                        pil_image = Image.open(image_path)
                        # Resize to fit (adjust size as needed)
                        pil_image = pil_image.resize((300, 225), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(pil_image)
                    else:
                        print(f"--- DEBUG: No image files found in {image_dir} ---")
                except Exception as img_e:
                    print(f"--- ERROR loading local image from {image_dir}: {img_e} ---")

            # --- Fallback to Web Image ---
            if not photo:
                print(f"--- DEBUG: Local image failed or not found for {pose_name}, trying web ---")
                photo = get_image_from_web(pose_name) # get_image_from_web should still be defined

            # --- Update Image Label ---
            if photo:
                img_label_detail.config(image=photo, text="")
                img_label_detail.image = photo # Keep reference
            else:
                img_label_detail.config(image="", text="Image not available")
                img_label_detail.image = None

            # --- Update YouTube Link ---
            youtube_links = asana_info.get("youtube_links", [])
            valid_links = [link for link in youtube_links if link.get("url") and link.get("title")]

            # Clear previous bindings first
            try:
                 # Using bindtags allows removing specific bindings without affecting default ones
                 current_tags = list(yt_link_label.bindtags())
                 if "yt_link_binding" in current_tags:
                     current_tags.remove("yt_link_binding")
                     yt_link_label.bindtags(tuple(current_tags))
                 # Remove the binding class itself if it exists
                 yt_link_label.bind_class("yt_link_binding", "<Button-1>", "")
            except tk.TclError:
                 pass # Ignore if tags don't exist


            if valid_links:
                yt_link = valid_links[0] # Use the first valid link
                yt_title = yt_link.get("title")
                yt_url = yt_link.get("url")

                yt_link_label.config(text=yt_title, foreground="blue", cursor="hand2")

                # Define a binding tag and apply it
                binding_tag = "yt_link_binding"
                yt_link_label.bind_class(binding_tag, "<Button-1>", lambda e, url=yt_url: open_url(url))
                # Add the binding tag to the widget's bindtags
                current_tags = list(yt_link_label.bindtags())
                if binding_tag not in current_tags:
                    yt_link_label.bindtags(tuple(current_tags) + (binding_tag,))

            else:
                yt_link_label.config(text="YouTube Link N/A", foreground="grey", cursor="")


            # --- Manage Camera ---
            if not camera_active:
                print("--- DEBUG: Calling start_camera_feed() ---")
                start_camera_feed(camera_status)
            elif cap and not cap.isOpened():
                 print("--- DEBUG: Camera stopped unexpectedly, calling start_camera_feed() ---")
                 start_camera_feed(camera_status)

        except Exception as e:
             print(f"--- ERROR in display_pose_details for {pose_name}: {e} ---")
             traceback.print_exc()

    def create_pose_label(parent, pose_name):
        # Indented block for this function
        print(f"--- DEBUG: create_pose_label called for '{pose_name}' with parent {parent}")
        # Ensure text= keyword argument is used
        label = ttk.Button(parent,
                           text=pose_name, # Added text=
                           command=lambda p=pose_name: display_pose_details(p),
                           style="Link.TButton")
        label.pack(anchor="w", fill='x', padx=5, pady=1)
        print(f"--- DEBUG: Packed pose button for '{pose_name}' into parent")

    def create_toggle_section(parent, title, poses):
        # Indented block for this function
        print(f"--- DEBUG: create_toggle_section called for '{title}' with parent {parent}")
        frame = ttk.Frame(parent)

        header_frame = ttk.Frame(frame)
        header_frame.pack(fill="x")

        poses_frame = ttk.Frame(frame) # Holds the pose buttons

        is_expanded = tk.BooleanVar(value=False)

        def toggle():
            print(f"\n--- DEBUG: Toggle CALLED for '{title}'. Current state: {is_expanded.get()}")
            if is_expanded.get():
                print(f"--- DEBUG: Collapsing '{title}'. Calling pack_forget() on {poses_frame}")
                poses_frame.pack_forget()
                is_expanded.set(False)
                toggle_btn.config(text=f"{title} ▼")
            else: # Expanding
                print(f"--- DEBUG: Expanding '{title}'. Packing poses_frame: {poses_frame}")
                if not poses_frame.winfo_children() and poses:
                     print(f"--- DEBUG: Populating poses_frame for '{title}' with: {poses}")
                     for pose in poses:
                         create_pose_label(poses_frame, pose)

                poses_frame.pack(fill="x", padx=10, pady=5)
                is_expanded.set(True)
                toggle_btn.config(text=f"{title} ▲")

                # ***** ADD UPDATE HERE *****
                # Force Tkinter to process pending events and update layout
                tab.update_idletasks()
                # *************************

                print(f"--- DEBUG: poses_frame children after pack: {poses_frame.winfo_children()}")
                if poses_frame.winfo_children():
                      # Check mapped status AFTER update_idletasks
                      print(f"--- DEBUG: First child mapped status (after update): {poses_frame.winfo_children()[0].winfo_ismapped()}")

        toggle_btn = ttk.Button(header_frame, text=f"{title} ▼", command=toggle)
        toggle_btn.pack(fill="x", padx=10, pady=5)

        # Populate poses_frame initially or during toggle (current logic populates in toggle if needed)
        # If you always want them created at startup, move the loop here:
        # if poses:
        #     for pose in poses:
        #         create_pose_label(poses_frame, pose)

        frame.pack(fill="x", padx=5, pady=5, anchor="n") # Pack the main section frame
        print(f"--- DEBUG: Packed section frame for '{title}' into parent")

    # --- Lessons Data (Still manually defined for UI structure) ---
    lessons = {
        "🧘‍♂️ 1. Beginner-Friendly Poses": [
            "Balasana (Child's Pose)", # String MUST exactly match a key in asana_data
            "Bitilasana (Cow Pose)",
            "Marjaryasana (Cat Pose)",
            "Tadasana (Mountain Pose)",
            "Padmasana (Lotus Pose)",
            "Baddha Konasana (Butterfly Pose)",
            "Sivasana (Corpse Pose)",
            "Utkatasana (Chair Pose)",
            "Vrksasana (Tree Pose)",
            "Trikonasana (Triangle Pose)",
            "Virabhadrasana One / Two (Warrior I / II)"
        ],

        "🧘‍♀️ 2. Good for Flexibility": [
            "Hanumanasana (Monkey Pose)",
            "Upavistha Konasana (Wide-Angle Seated Forward Bend)",
            "Uttanasana (Standing Forward Bend)",
            "Parsvottanasana (Pyramid Pose)",
            "Paschimottanasana (Seated Forward Bend)",
            "Urdhva Dhanurasana (Upward-Facing Bow Pose)",
            "Halasana (Plow Pose)",
            "Eka Pada Rajakapotasana (One-Legged King Pigeon Pose)",
            "Ardha Chandrasana (Half Moon Pose)",
            "Ardha Matsyendrasana (Half Lord of the Fishes Pose)"
        ],
        "🧍 3. Good for Spine & Back": [
            "Dhanurasana (Bow Pose)",
            "Urdhva Mukha Svsnssana (Upward-Facing Dog Pose)",
            "Salamba Bhujangasana (Sphinx Pose)",
            "Setu Bandha Sarvangasana (Bridge Pose)",
            "Ardha Matsyendrasana (Half Lord of the Fishes Pose)",
            "Ustrasana (Camel Pose)",
            "Camatkarasana (Wild Thing Pose)",
            "Bitilasana (Cow Pose)",
            "Marjaryasana (Cat Pose)"
        ],
        "🧎 4. Great for Core Strength": [
            "Navasana (Boat Pose)",
            "Ardha Navasana (Half Boat Pose)",
            "Phalakasana (Plank Pose)",
            "Vasisthasana (Side Plank Pose)",
            "Utkatasana (Chair Pose)"
        ],
        "   5. Knee-Friendly / Strengthen Knees": [
            "Utkatasana (Chair Pose)",
            "Virabhadrasana One (Warrior I)",
            "Virabhadrasana Two (Warrior II)",
            "Virabhadrasana Three (Warrior III)",
            "Trikonasana (Triangle Pose)",
            "Utthita Parsvakonasana (Extended Side Angle Pose)",
            "Utthita Hasta Padangusthasana (Extended Hand-to-Big-Toe Pose)"
        ],
        "🧠 6. Good for Balance & Focus": [
            "Vrksasana (Tree Pose)",
            "Ardha Chandrasana (Half Moon Pose)",
            "Garudasana (Eagle Pose)",
            "Utthita Hasta Padangusthasana (Extended Hand-to-Big-Toe Pose)",
            "Vasisthasana (Side Plank Pose)",
            "Bakasana (Crow Pose)",
            "Pincha Mayurasana (Feathered Peacock Pose)",
            "Adho Mukha Vrksasana (Handstand)"
        ],
        "🛏️ 7. Relaxation & Cooling Down": [
            "Balasana (Child's Pose)",
            "Sivasana (Corpse Pose)",
            "Supta Kapotasana (Reclining Pigeon Pose)",
            "Baddha Konasana (Butterfly Pose)",
            "Halasana (Plow Pose)"
        ]
    }
    # --- Style Definition ---
    # ... (rest of the function) ...

    # --- Populate the list UI (using the manual 'lessons' dictionary) ---
    print("\n--- DEBUG: Starting UI Population Loop ---") # Add newline for clarity
    if lessons:
        for title, pose_name_list_from_lessons_dict in lessons.items():
            print(f"\n--- DEBUG: Processing Category: '{title}' ---") # Add quotes
            print(f"--- DEBUG: Poses listed in lessons dict: {pose_name_list_from_lessons_dict}")

            # Filter list to only include poses found in asana_data
            valid_poses_in_category = []
            poses_not_found = [] # Keep track of mismatches
            for pose_name in pose_name_list_from_lessons_dict:
                if pose_name in asana_data:
                    valid_poses_in_category.append(pose_name)
                else:
                    poses_not_found.append(pose_name) # Add to list for summary

            # Print summary of mismatches for this category
            if poses_not_found:
                 print(f"--- WARNING: The following poses from the lessons list were NOT FOUND in asana_data keys for '{title}':")
                 for pname in poses_not_found:
                     print(f"    - '{pname}'") # Print with quotes to see whitespace issues

            print(f"--- DEBUG: Valid poses found in asana_data for this category: {valid_poses_in_category}")

            if valid_poses_in_category:
                 print(f"--- DEBUG: Calling create_toggle_section for: '{title}' with {len(valid_poses_in_category)} valid poses.")
                 # Pass ONLY the valid poses list to the UI creation function
                 create_toggle_section(scrollable_frame, title, valid_poses_in_category)
            else:
                 print(f"--- WARNING: Skipping UI section for '{title}' because no valid poses were found in asana_data. ---")
    else:
        print("--- DEBUG: Lessons dictionary (for UI) is empty! ---")
    print("\n--- DEBUG: Finished UI Population Loop ---")

    return tab

last_speech_time = 0
SPEECH_COOLDOWN = 4  # seconds between voice feedback

