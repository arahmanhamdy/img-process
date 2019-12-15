from PIL import Image
import numpy as np


NAME = "Average Pixel Value"


def execute(img_obj):
    image = Image.open(img_obj)
    return np.mean(image)
