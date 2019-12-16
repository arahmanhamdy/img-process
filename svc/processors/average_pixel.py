from PIL import Image
import numpy as np

# This name will be added as a key to processing results dict
NAME = "Average Pixel Value"


def execute(img_obj):
    """
    Gets the mean pixel value for an image
    This method is being called from Image Controller
    :param img_obj: holds the stream of uploaded image (type:werkzeug.datastructures.FileStorage)
    :return: result which will be serialized and added to the response of upload endpoint
    """
    image = Image.open(img_obj)
    return np.mean(image)
