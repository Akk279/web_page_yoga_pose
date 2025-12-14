import tensorflow as tf

# Load the saved model
model = tf.keras.models.load_model("yoga_pose_classifier.keras")

# Display model summary
model.summary()
