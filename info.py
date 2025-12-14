import tensorflow as tf

model = tf.keras.models.load_model("yoga_pose_classifier.keras")

# 1. Print model type
print("Model class:", type(model))

# 2. Print model summary (architecture)
model.summary()

# 3. Show model input/output shapes
print("\nInput shape:", model.input_shape)
print("Output shape:", model.output_shape)

# 4. Check if it's Sequential or Functional
if isinstance(model, tf.keras.Sequential):
    print("✅ This is a Sequential model")
else:
    print("✅ This is a Functional or subclassed model")
