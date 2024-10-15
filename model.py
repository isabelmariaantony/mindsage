# Correct import for VGG16 preprocessing in TensorFlow 2.x

import tensorflow as tf
import numpy as np
import keras


# Path of the saved model
loaded_model = tf.keras.models.load_model('models/best_model_vgg16.h5')


def predict(img_path):
    """
    This function takes a PIL Image object, preprocesses it, 
    and returns the predicted class index.
    """
    img = keras.preprocessing.image.load_img(img_path, target_size=(224,224))
    img_array = keras.preprocessing.image.img_to_array(img)
    img_batch = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_preprocessed = keras.applications.vgg16.preprocess_input(img_batch)

    # Perform prediction
    prediction = loaded_model.predict(img_preprocessed)

    # Return the index of the highest probability
    return np.argmax(prediction)