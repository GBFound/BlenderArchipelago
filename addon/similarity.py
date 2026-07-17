import bpy
import numpy
from . import utils

def _get_image_pixels(image: bpy.types.Image) -> numpy.ndarray:
    image.update()
    w, h = image.size[0], image.size[1]
    pixels = numpy.empty(w * h * 4, dtype=numpy.float32)
    image.pixels.foreach_get(pixels)

    return pixels.reshape(h, w, 4)


def compare_images(img_a: bpy.types.Image, img_b: bpy.types.Image) -> float:
    """
    Compare two images using a similar algorithm as Paint AP
    Returns 0.0 if either image has no data.
    """

    if img_a.size[0] != img_b.size[0] or img_a.size[1] != img_b.size[1]:
        utils.queue_popup("Image resolutions do not match.")
        return 0.0

    if img_a.size[0] == 0 or img_b.size[0] == 0:
        utils.queue_popup("One or both images have no size.")
        return 0.0

    if len(img_a.pixels) == 0 or len(img_b.pixels) == 0:
        utils.queue_popup("One or both images have no pixel data.")
        return 0.0

    pixels_a = _get_image_pixels(img_a)
    pixels_b = _get_image_pixels(img_b)

    h = pixels_a.shape[0]
    w = pixels_a.shape[1]

    # :3 removes alpha channel
    a_rgb = pixels_a[:h, :w, :3]
    b_rgb = pixels_b[:h, :w, :3]
    
    # Only alpha
    a_alpha = pixels_a[:h, :w, 3]
    b_alpha = pixels_b[:h, :w, 3]

    # Per-pixel euclidean distance across RGB channels
    difference_squared_pixels = (a_rgb - b_rgb) ** 2
    similarity_pixels = 1 - numpy.sqrt(difference_squared_pixels.sum(axis=2) / 3)

    # Shifts range from [0,1] to [-1,1]
    similarity_pixels = 2 * similarity_pixels - 1

    # Zero out any pixel where either image was transparent to treat them as a neutral match because of the progressive render sizes
    transparent_mask = (a_alpha == 0) | (b_alpha == 0)
    similarity_pixels[transparent_mask] = 0

    similarity = similarity_pixels.mean() * 100

    return round(similarity, 3)
