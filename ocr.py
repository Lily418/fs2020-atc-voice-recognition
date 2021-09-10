from PIL import Image, ImageOps
import pytesseract



atc = Image.open('atc.png')

width = atc.size[0] 
height = atc.size[1] 
for i in range(0,width):# process all pixels
    for j in range(0,height):
        data = atc.getpixel((i,j))
        # print(data)
        if data[0] == 255 and data[1] == 75 and data[2] == 0:
            atc.putpixel((i,j),(255, 255, 255))

atc1 = pytesseract.image_to_string(atc, lang='eng', config=r'--psm 6 -c tessedit_write_images=true')

print(atc1)