from wand.image import Image as WandImage
from wand.display import display
from wand.drawing import Drawing
from wand.color import Color
from PIL import Image, ImageFilter, ImageFont, ImageDraw

import uuid
import sys

def create_img(arg1, arg2, arg3):
    img_width = 600
    img_height = 200

    text1 = arg1
    text1_font = 50
    text1_x = (img_width/2) - (len(text1) * 18 )
    text1_y = 80

    text2 = arg2
    text2_font = 20
    text2_x = (img_width/2) - (len(text2) * 6 )
    text2_y = 120

    text3 = arg3
    text3_font = 20
    text3_x = (img_width/2) - (len(text3) * 5)
    text3_y = img_height - 50

    folder = "tmp/"
    tmp_text_file = folder + str(uuid.uuid4()) + ".png"
    tmp_img_file = folder + str(uuid.uuid4()) + ".png"

    # CREATING DROPSHADOW
    #==============================

    image = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("LibreBaskerville-Regular.ttf", text1_font)

    n = 0
    while n < 20:
        draw.text((text1_x + n + 2, text1_y-40 + n + 2), text1, (120+n*5, 120+n*5, 120+n*5), font=font)
        if n > 15:
            image = image.filter(ImageFilter.BLUR)
        n += 1

    image.save(tmp_img_file)

    # CREATING EMBOSSED TEXT
    #================================
    image = Image.new('RGBA',(img_width, img_height))
    draw = ImageDraw.Draw(image)
    text = draw.text((text1_x, text1_y-40), text1, ('#26343F') , font=font)
    image.save(tmp_text_file, transparency=0)

    command = "./bevel.sh -w 10 -f inner -o raised {0} {0}".format(tmp_text_file)

    import subprocess
    subprocess.check_output(['bash','-c', command])

    text = Image.open(tmp_text_file)
    edit1_img = Image.open(tmp_img_file)
    edit1_img.paste(text, (0, 0), text)
    edit1_img.save(tmp_img_file, 'PNG')

    # CREATING OTHER WORDS
    #===============================

    with Drawing() as draw:

        draw.font = 'Calibri.ttf'
        draw.font_size = text2_font
        draw.fill_color = Color('#222324')
        text2 = " ".join(text2)
        draw.text(text2_x, text2_y, text2)

        draw.font = 'matura-mt-script.ttf'
        draw.font_size = text3_font
        draw.fill_color = Color('#7F9DAC')
        draw.text(text3_x, text3_y, text3)

        with WandImage(filename=tmp_img_file) as img:
            draw.draw(img)
            img.save(filename=tmp_img_file)
            return tmp_img_file
