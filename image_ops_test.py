from PIL import Image, ImageOps

ImageOps.invert(Image.open('atc.png')).save("./atc.png", "PNG")
