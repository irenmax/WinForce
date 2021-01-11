import os
from PIL import Image, ImageOps
import cv2
import numpy as np
import tensorflow.keras

np.set_printoptions(suppress=True)


def pad_img(img):
    size = max(img.shape)
    height, width, _ = img.shape

    def pad(x): return int((size - x) / 2)
    return cv2.copyMakeBorder(
        img,
        pad(height),
        pad(height),
        pad(width),
        pad(width),
        cv2.BORDER_CONSTANT)


def predict(img):
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    size = (224, 224)
    image = Image.fromarray(img)
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

print('starting video...')
cap = cv2.VideoCapture(0)
cv2.namedWindow("halo", cv2.WINDOW_NORMAL)

while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print('k bye')
        quit()

    _, frame = cap.read()
    flipped = cv2.flip(frame, 1)

    img = pad_img(flipped)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    cv2.imshow('halo', rgb)

    pred = predict(img)
    print(labels[pred.argmax()])


cap.release()
cv2.destroyAllWindows()
