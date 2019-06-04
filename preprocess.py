import os
import traceback
import configparser
from tqdm import tqdm

import Preprocessing.config as config
from Preprocessing.display import draw_circles
from Preprocessing.processing import pupil_recognition, iris_recognition, segmentation
from Preprocessing.utils import load_image, resize_segments, save_segments, check_folders, get_average_shape, crop_image


def create_data(path):
    cropped_array = []
    skipped_count = 0
    images = load_image(path, extention=config.UTILS.get('IMAGE_EXTENTION'), resize=config.UTILS.getboolean(
        'RESIZE'), resize_shape=config.UTILS.getint('RESIZE_SHAPE'))
    for img in tqdm(images):
        try:
            pupil_circle = pupil_recognition(img, thresholdpupil=config.PREPROCESSING.getint('THRESHOLD_PUPIL'), incBright=config.FILTERING_PUPIL.getboolean(
                'INCREASE_BRIGHTENESS'), adjGamma=config.FILTERING_PUPIL.getboolean('ADJUST_GAMMA'))
            iris_circle = iris_recognition(img, thresholdiris=config.PREPROCESSING.getint('THRESHOLD_IRIS'), incBright=config.FILTERING_IRIS.getboolean(
                'INCREASE_BRIGHTENESS'), adjGamma=config.FILTERING_IRIS.getboolean('ADJUST_GAMMA'))

            segmented_image, mask = segmentation(
                img, iris_circle, pupil_circle, startangle=config.PREPROCESSING.getint(
                    'STARTANGLE'),
                endangle=config.PREPROCESSING.getint('ENDANGLE'))
            # cv2.imshow('Segmented image', segmented_image)

            cropped_image = crop_image(
                segmented_image, offset=config.UTILS.getint('CROP_OFFSET'),
                tollerance=config.UTILS.getint('CROP_TOLLERANCE'))
            cropped_array.append(cropped_image)
            # cv2.imshow('Cropped image', cropped_image)

            draw_circles(img, pupil_circle, iris_circle)
            # show_images(img)
        except Exception:
            skipped_count += 1
            traceback.print_exc()
            continue

    print('\n')
    print('Skipped', skipped_count, 'images')
    return cropped_array


def main():
    try:
        config.load_config_file('./config.ini')

    except KeyError as e:
        print('File di configurazione non corretto: manca la sezione', e)
        return
    except Exception as e:
        traceback.print_exc()
        return

    DATADIR = "./DATA_IMAGES"
    CATEGORIES = ['DB_PROBS', 'DB_NORMAL']
    cropped_dict = {}

    if check_folders(DATADIR) is False:
        raise Exception(
            'Non sono presenti immagini nelle cartelle DB_PROBS e/o DB_NORMAL')

    for category in tqdm(CATEGORIES):
        data_path = os.path.join(DATADIR, category)
        cropped_dict[category] = create_data(data_path)

    average_shape = get_average_shape(cropped_dict)

    print('Resizing and saving segments...')
    for category in tqdm(CATEGORIES):
        resized_segments = resize_segments(
            cropped_dict[category], average_shape)
        save_segments(resized_segments, category)


if __name__ == '__main__':
    main()
