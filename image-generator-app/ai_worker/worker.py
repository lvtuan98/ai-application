from flask import Flask, request, jsonify, send_file
from utils.image_processor import create_image
from io import BytesIO
from flask_cors import CORS
from config import Config
import base64

app = Flask(__name__)
CORS(app, origins="*")
app.config.from_object(Config)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        data = "This is AI-worker"
        return jsonify({"data": data})


@app.route("/generate", methods=["POST"])
def generate_image():
    try:
        data = request.get_json()
        print(data)
        text = data.get("text")
        print("text", text)
        options = data.get("options", {})
        print("options", options)

        image = create_image(text, options)
        img_io = BytesIO()
        image.save(img_io, "PNG")
        img_io.seek(0)
        print("here")
        encoded_image = base64.b64encode(img_io.getvalue())
        print(type(encoded_image))
        return encoded_image
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
