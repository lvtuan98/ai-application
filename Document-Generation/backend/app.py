from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    return jsonify({'filepath': filepath})

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    filepath = data['filepath']
    start_point = tuple(data['start_point'])
    end_point = tuple(data['end_point'])

    # Load the image and draw the bounding box
    image = cv2.imread(filepath)
    cv2.rectangle(image, start_point, end_point, (0, 255, 0), 2)

    # Save the image with bounding box
    output_path = os.path.join(UPLOAD_FOLDER, 'output_' + os.path.basename(filepath))
    cv2.imwrite(output_path, image)

    return jsonify({'output_path': output_path, 'start_point': start_point, 'end_point': end_point})

if __name__ == '__main__':
    app.run(debug=True)
