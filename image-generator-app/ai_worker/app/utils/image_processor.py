from PIL import Image, ImageDraw, ImageFont

def generate_image(text, options):
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()
    text_width, text_height = draw.textsize(text, font=font)
    position = ((width - text_width) // 2, (height - text_height) // 2)

    draw.text(position, text, fill='black', font=font)

    return image