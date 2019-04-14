from pyganim import getImagesFromSpriteSheet
import os


def init_image(filename_t, filename_d):
    images_l_r = getImagesFromSpriteSheet(os.getcwd() + filename_t, rows=2, cols=3)

    x_e = int(len(images_l_r) / 2)

    images_l = [images_l_r[i] for i in range(x_e)]
    images_r = [images_l_r[i] for i in range(x_e, len(images_l_r))]
    images_t_d = getImagesFromSpriteSheet(os.getcwd() + filename_d, rows=2, cols=3)
    images_d = [images_t_d[i] for i in range(x_e)]
    images_t = [images_t_d[i] for i in range(x_e, len(images_t_d))]

    images_dic = {"UP": images_t, "DOWN": images_d, "LEFT": images_l, "RIGHT": images_r}

    return images_dic


def convert_images(*args):

    for dic in args:
        for keys, list_images in dic.items():
            for i, image in enumerate(list_images):
                dic[keys][i] = image.convert()


image_data_original = {"Player": None, "Bullet": None, "Enemy": None, "Bonus": None}
