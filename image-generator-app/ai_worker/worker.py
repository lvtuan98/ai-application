from flask import Flask, request, jsonify, send_file
from utils.image_processor import create_image
from io import BytesIO
from flask_cors import CORS
import base64
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app, origins="*")


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        data = "This is AI-worker"
        return jsonify({"data": data})


@app.route("/generate", methods=["POST"])
def generate_image():
    try:
        data = request.get_json()
        print(data, flush=True)
        text = data.get("text")
        options = data.get("options", {})

        image = create_image(text, options)
        img_io = BytesIO()
        image.save(img_io, "PNG")
        img_io.seek(0)
        encoded_image = base64.b64encode(img_io.getvalue())
        return encoded_image
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(host=os.environ.get("AI_WORKER_HOST"), 
            port=int(os.environ.get("AI_WORKER_PORT")), 
            debug=os.environ.get("DEBUG"))
