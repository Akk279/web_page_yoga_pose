import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# Define paths
BASE_DIR = r"F:\vs studio code\yoga\YOGA_NEW_DATASET"
train_dir = os.path.join(BASE_DIR, "train")
val_dir = os.path.join(BASE_DIR, "val")

# Data Augmentation for training
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=15,
    zoom_range=0.2,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Validation data (no augmentation)
val_datagen = ImageDataGenerator(rescale=1./255)

# Data generators
train_gen = train_datagen.flow_from_directory(train_dir, target_size=(224, 224), batch_size=32, class_mode='categorical')
val_gen = val_datagen.flow_from_directory(val_dir, target_size=(224, 224), batch_size=32, class_mode='categorical')

# Load MobileNetV2 without the top layer
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Freeze base model initially
base_model.trainable = False

# Add custom top layers
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
y_pred = Dense(train_gen.num_classes, activation='softmax')(x)

# Build and compile model
model = Model(inputs=base_model.input, outputs=y_pred)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Initial training
model.fit(train_gen, validation_data=val_gen, epochs=10)

# 🔓 Unfreeze more layers of the base model for fine-tuning
for layer in base_model.layers[-50:]:  # Unfreeze the last 50 layers
    layer.trainable = True

# Recompile with a lower learning rate
model.compile(optimizer=tf.keras.optimizers.Adam(1e-6), loss='categorical_crossentropy', metrics=['accuracy'])

# Fine-tune the model with more epochs
model.fit(train_gen, validation_data=val_gen, epochs=20)  # Increase epochs to 20

# Save the fine-tuned model
model.save("yoga_pose_finetuned_model_v2.keras")
