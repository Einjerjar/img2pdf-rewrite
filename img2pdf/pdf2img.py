import fitz
from PIL import Image


def parse_images(pdf_source: str, zoom=1.0, color_format='RGB'):
    pdf = fitz.Document(pdf_source)
    pdf_matrix = fitz.Matrix(zoom, zoom)

    img_list = []

    for page in pdf:
        pix_map = page.get_pixmap(matrix=pdf_matrix)

        img = Image.frombytes(color_format, [pix_map.width, pix_map.height], pix_map.samples)

        img_list.append(img)

    return img_list
