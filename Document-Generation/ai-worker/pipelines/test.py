import os
from pathlib import Path
import numpy as np
from PIL import Image, ImageFont, ImageDraw

cur_path = str(Path(__file__).parents[0])

def draw_text(text): 
    font_size = 40
    font_file = os.path.join(cur_path, 'fonts/arialuni.ttf')
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