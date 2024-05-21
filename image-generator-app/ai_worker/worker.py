from flask import Flask, request, jsonify
from utils.image_processor import create_image
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5002"])


@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        text = data.get('text')
        options = data.get('options', {})

        image = create_image(text, options)
        img_io = BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
