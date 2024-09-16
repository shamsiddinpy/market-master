from PIL import Image


def resize_image(image_path, size):
    with Image.open(image_path) as img:
        img = img.resize(size, Image.Resampling.LANCZOS)
        img.save(image_path, quality=95)
