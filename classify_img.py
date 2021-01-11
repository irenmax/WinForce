import os
from PIL import Image, ImageOps
import numpy as np
import tensorflow.keras

np.set_printoptions(suppress=True)


def predict(img_path):
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    size = (224, 224)
    image = Image.open(img_path)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array
    prediction = model.predict(data)
    return prediction


print('reading labels...')
labels = {}
for line in open(os.path.join('model', 'labels.txt'), 'r').readlines():
    k_v = line.split(' ')
    labels[int(k_v[0])] = k_v[1][:-1]

print('loading model...')
model = tensorflow.keras.models.load_model(
    os.path.join('model', 'keras_model.h5'), compile=False)
print('\n')
which = input('which kind? (left, right, middle, none): ')
nr = input('nr?: ')

img_path = os.path.join(which, f'{nr}.jpg')
pred = predict(img_path)
print(labels[pred.argmax()])
