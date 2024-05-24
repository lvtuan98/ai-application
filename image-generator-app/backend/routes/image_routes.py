from flask import Blueprint, request, jsonify
from tasks.image_tasks import generate_image_task
from config import Config
import requests


image_bp = Blueprint('image_bp', __name__)

@image_bp.route('/generate', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        print(data)
        # task = generate_image_task.apply_async(args=[data])
        # print("task_id", task.id)
        # return jsonify({"task_id": task.id}), 202
        response = requests.post(f"{Config.AI_WORKER_URL}/generate", json={
            "text": data['data'],
            "options": ""
        })
        print(type(response.content))
        return response.content, response.status_code
        
    except Exception as e:
        print({"error": str(e)}, 500)
        return {"error": str(e)}, 500

@image_bp.route('/status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = generate_image_task.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        return jsonify({"status": task.state, "result": task.result}), 200
    else:
        return jsonify({"status": task.state}), 200
