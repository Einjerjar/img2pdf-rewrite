# Img2PDF (rewrite)
A rewrite of the previous [img2pdf.py](https://github.com/Einjerjar/img2pdf.py) project, lots of features have been stripped leaving only the bare necessities, being `img2pdf` and `pdf2img`, which should be self-explanatory.

Also, this is more of a wrapper for the awesome [PyMuPDF](https://github.com/pymupdf/PyMuPDF) library.

### Notes
A gui implementation making use of the [DearPyGUI](https://github.com/hoffstadt/DearPyGui) library framework is included, containing all (?) the previously planned features, including the ability to merge pdfs and images, rearrange pages, preview pages, and some other stuff (?).

Said GUI implementation was the real target for this project, which has now been achieved, as such, there will likely no longer be any updates, other than bugfixes, and some final polish (?).

### Usage
Convert images in a folder to a pdf
```python
import img2pdf as i2p
import os

target_extensions = ['jpg', 'jpeg', 'png', 'webp']
files = [x for x in os.listdir('source_folder') if os.path.splitext(x)[1][1:] in target_extensions]

i2p.gen_pdf(files, 'out.pdf')
```

Parse pdf pages as a PIL Image array
```python
images = i2p.parse_images('target.pdf')
```

Convert PIL Image array to pdf
```python
images = [...]
i2p.gen_pdf(images, 'out.pdf')
```

### Todo
- CLI support
- Try to figure out if PIL Images can be fed directly to DPG's draw_image (when no longer lazy).
- Add polish to the GUI (?). 
- Make it an installable package, and upload to PyPi or sumtn.

### Send support :3
<a href='https://ko-fi.com/X8X831J1L' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://cdn.ko-fi.com/cdn/kofi1.png?v=2' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>