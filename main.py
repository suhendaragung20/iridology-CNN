import os
import cv2
from iris_recog import iris_recognition, pupil_recognition
from display import draw_circles, show_images


def load_image(path):
    # global images
    # global real_images
    # global images_names
    images = []
    images_names = []
    for file in os.listdir(path):
        title = file.title().lower()
        if title.split('.')[-1] == 'jpg':
            images_names.append(title)
            images.append(cv2.imread(os.path.join(path, title)))
    return images


def main(path):
    images = load_image(path)
    for img in images:
        pupil_circles = pupil_recognition(img)
        iris_circles = iris_recognition(img)
        draw_circles(img, pupil_circles, iris_circles)
        show_images(img)


main('C:\\Users\\Albe\\Desktop\\tesi-triennale\\images')
