from flask import Flask, url_for
from flask import render_template
from flask import request
from flask import redirect

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
    text1_y = 40

    text2 = arg2
    text2_font = 20
    text2_x = (img_width/2) - (len(text2) * 6 )
    text2_y = 120

    text3 = arg3
    text3_font = 20
    text3_x = (img_width/2) - (len(text3) * 5)
    text3_y = img_height - 50

    folder = "static/"
    tmp_text_file = folder + str(uuid.uuid4()) + ".png"
    tmp_img_file = folder + str(uuid.uuid4()) + ".png"

    # CREATING DROPSHADOW
    #==============================

    image = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("./static/fonts/LibreBaskerville-Regular.ttf", text1_font)
    x, y = draw.textsize(text1, font=font)

    # make sure text is within box
    while x > 600:
        text1_font -= 1
        font = ImageFont.truetype("./static/fonts/LibreBaskerville-Regular.ttf", text1_font)
        x, y = draw.textsize(text1, font=font)

    text1_x = img_width/2 - (int(x)/2)

    # draw the shadow by moving and drawing the text to the bottom right for 20 iterations
    # and also making it lighter as we iterate
    n = 0
    while n < 20:
        draw.text((text1_x + n + 2, text1_y + n + 2), text1, (120+n*5, 120+n*5, 120+n*5), font=font)
        if n > 15:
            image = image.filter(ImageFilter.BLUR)
        n += 1

    image.save(tmp_img_file)

    # CREATING EMBOSSED TEXT
    #================================
    image = Image.new('RGBA',(img_width, img_height))
    draw = ImageDraw.Draw(image)
    x, y = draw.textsize(text1, font=font)

    while x > 600:
        text1_font -= 1
        font = ImageFont.truetype("./static/fonts/LibreBaskerville-Regular.ttf", text1_font)
        x, y = draw.textsize(text1, font=font)

    text1_x = img_width/2 - (int(x)/2)
    text = draw.text((text1_x, text1_y), text1, ('#26343F') , font=font)
    image.save(tmp_text_file, 'PNG')

    # Uses 3rd party bevel script that uses imagemagick to add effects
    command = "./lib/bevel.sh -w 10 -f inner -o raised {0} {0}".format(tmp_text_file)

    import subprocess
    subprocess.check_output(['bash','-c', command])

    text = Image.open(tmp_text_file)
    edit1_img = Image.open(tmp_img_file)
    edit1_img.paste(text, (0, 0), text)
    edit1_img.save(tmp_img_file, 'PNG')

    # CREATING OTHER WORDS
    #===============================

    with Drawing() as draw:
        with WandImage(filename=tmp_img_file) as img:

            draw.font = './static/fonts/Calibri.ttf'
            draw.font_size = text2_font
            draw.fill_color = Color('#222324')
            text2 = " ".join(text2)
            x = draw.get_font_metrics(img, text2)[11] #12th is the x in the metric
            text2_x = (img_width/2) - (int(x)/2)
            draw.text(text2_x, text2_y, text2)

            draw.font = './static/fonts/matura-mt-script.ttf'
            draw.font_size = text3_font
            draw.fill_color = Color('#7F9DAC')
            x = draw.get_font_metrics(img, text3)[11] #12th is the x in the metric
            text3_x = (img_width/2) - (int(x)/2)
            draw.text(text3_x, text3_y, text3)

            draw.draw(img)
            img.save(filename=tmp_img_file)
            return tmp_img_file.replace("static/", "")

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def mainpage():
    error = None
    if request.method == 'POST':
        if request.form['text1'] is None:
            error = 'Insert something dude'
        elif request.form['text2'] is None:
            error = 'Insert something else too'
        elif request.form['text3'] is None:
            error = 'Insert here as well'
        else:
            text1 = request.form['text1']
            text2 = request.form['text2']
            text3 = request.form['text3']
            if not (text1 and text2 and text3):
                img = None
            else:
                img = create_img(text1, text2, text3)

            return redirect(url_for('picture', img=img))
    return render_template('form.html', error=error)

@app.route('/picture/')
@app.route('/picture/<img>')
def picture(img=None):
    if img is not None:
        path = img
    else:
        path="default.jpg"
    return render_template('picture.html', img=path)

if __name__ == '__main__':
    app.run(Debug=True)


