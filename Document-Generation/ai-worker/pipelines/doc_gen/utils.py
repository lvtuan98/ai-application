import numpy as np
from PIL import Image, ImageFont, ImageDraw


def draw_text(im_shape, text): 
    font_size = 40
    font_file = 'fonts/arialuni.ttf'
    len_text = len(text)
    if len_text == 0:
        len_text = 3
    img = Image.new('RGB', ((len_text+2)*font_size, 60), color='white')  
    # Define the font object
    font = ImageFont.truetype(font_file, font_size)
    # Define the text and position
    pos = (40, 10)

    draw = ImageDraw.Draw(img)
    draw.text(pos, text, font=font, fill='black')
    img = np.array(img)

    return img

def process_location(location, instance_image_size):    
    h = location[3]-location[1]
    location[3] = min(location[3]+h/10, instance_image_size[0]-1)
    return location

def generate_mask(im_shape, ocr_locate):
    mask = Image.new("L", im_shape, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle(
            (ocr_locate[0], ocr_locate[1], ocr_locate[2], ocr_locate[3]),
            fill=1,
        )
    mask = np.array(mask)
    return mask

def prepare_mask_and_masked_image(image, mask):
    masked_image = np.multiply(image, np.stack([mask < 0.5,mask < 0.5,mask < 0.5]).transpose(1,2,0))

    return masked_image


def grid_img(imgs, rows=1, cols=3, scale=1):
    assert len(imgs) == rows * cols

    w, h = imgs[0].size
    w, h = int(w*scale), int(h*scale)

    grid = Image.new('RGB', size=(cols*w, rows*h))
    grid_w, grid_h = grid.size

    for i, img in enumerate(imgs):
        img = img.resize((w,h))
        grid.paste(img, box=(i%cols*w, i//cols*h))
    return grid