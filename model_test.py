# Correct import for VGG16 preprocessing in TensorFlow 2.x

import tensorflow as tf
import numpy as np
import keras


# Path of the saved model
loaded_model = tf.keras.models.load_model('models/best_model_vgg16.h5')

img_path = 'images/verymild_2212.jpg'
img = keras.preprocessing.image.load_img(img_path, target_size=(224,224))
img_array = keras.preprocessing.image.img_to_array(img)
img_batch = np.expand_dims(img_array, axis=0)
img_preprocessed = keras.applications.vgg16.preprocess_input(img_batch)
prediction = loaded_model.predict(img_preprocessed)
print(prediction)
print(np.argmax(prediction))
