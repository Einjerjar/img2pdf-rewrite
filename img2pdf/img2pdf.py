from statistics import quantiles
from typing import List

from PIL import Image


def gen_pdf(source: List[Image.Image] or List[str], out_file: str, quality: int = 80, optimize: bool = True):
    img_list = source
    if type(source[0]) == str:
        img_list = [Image.open(x) for x in source]

    if not out_file.endswith('.pdf'):
        out_file += '.pdf'

    root = img_list.pop(0)
    root.save(out_file, save_all=True, append_images=img_list, optimize=optimize, quality=quality)
