from flask import request, send_file
from services.image_service import process_image
from io import BytesIO

def generate_image():
    try:
        data = request.get_json()
        text = data.get('text')
        options = data.get('options', {})

        image = process_image(text, options)
        img_io = BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return {"error": str(e)}, 500
