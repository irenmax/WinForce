import os
import glob
import cv2


def remove_temp():
    for name in os.listdir('temp'):
        os.remove(os.path.join(temp_dir, name))
    os.rmdir(temp_dir)


cap = cv2.VideoCapture(0)

dir_path = os.path.dirname(os.path.realpath(__file__))
temp_dir = os.path.join(dir_path, 'temp')

if not os.path.isdir(temp_dir):
    os.makedirs(temp_dir)

is_capturing = False
should_stop = False
img_nr = 0

cv2.namedWindow("halo", cv2.WINDOW_NORMAL)

print('''
press space to record, then press space to stop
press q to quit without saving
press s to save images
''')

while not (should_stop):
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print('k bye')
        remove_temp()
        quit()

    if cv2.waitKey(1) & 0xFF == ord('s'):
        should_stop = True

    _, frame = cap.read()
    flipped = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(flipped, cv2.COLOR_BGR2BGRA)

    cv2.imshow('halo', rgb)

    if cv2.waitKey(1) & 0xFF == ord(' '):
        is_capturing = not is_capturing
        if is_capturing:
            print('capturing on')
        else:
            print('capturing off')
            print(f'{img_nr} images taken (total)')

    if (is_capturing):
        cv2.imwrite(os.path.join(temp_dir, f'{img_nr}.jpg'), flipped)
        img_nr += 1

cap.release()
cv2.destroyAllWindows()


out = input('output directory name: ')
out_dir = os.path.join(dir_path, out)

if not os.path.isdir(out_dir):
    os.makedirs(out_dir)

print('processing...')

for fname in glob.glob(f'{temp_dir}/*.jpg'):
    img = cv2.imread(os.path.join(temp_dir, os.path.basename(fname)))

    size = max(img.shape)
    height, width, _ = img.shape

    def pad(x): return int((size - x) / 2)

    image = cv2.copyMakeBorder(
        img,
        pad(height),
        pad(height),
        pad(width),
        pad(width),
        cv2.BORDER_CONSTANT)
    cv2.imwrite(os.path.join(out_dir, os.path.basename(fname)), image)


remove_temp()
