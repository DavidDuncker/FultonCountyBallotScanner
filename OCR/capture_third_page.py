from PIL import Image, ImageSequence


def capture_third_page(path_to_image):
    image = Image.open(path_to_image)
    page_count = 0
    data_page = None
    for page in ImageSequence.Iterator(image):
        page_count += 1
        if page_count == 3:
            data_page = page
    return data_page