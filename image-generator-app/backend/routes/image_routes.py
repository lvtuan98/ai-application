import os
import requests
from flask import Blueprint, request, jsonify
from celery.result import AsyncResult
from tasks.image_tasks import generate_image_task
from dotenv import load_dotenv
load_dotenv()

AI_WORKER_URL = os.environ.get("AI_WORKER_URL")

image_bp = Blueprint('image_bp', __name__)

@image_bp.route('/generate', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        print(data, flush=True)
        input_data = {
            "text": data['data'],
            "options": ""
        }
        task = generate_image_task.apply_async(args=[input_data])
        print("task_id", task.id, flush=True)
        return jsonify({"task_id": task.id}), 202

        # response = requests.post(f"{AI_WORKER_URL}/generate", json=input_data, verify=False)
        # return response.content, response.status_code
        
    except Exception as e:
        return {"error": str(e)}, 500

@image_bp.route('/status/<task_id>', methods=['GET'])
def task_status(task_id):
    print("task_id", task_id, flush=True)
    task = generate_image_task.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        result = task.result
        response = {
            'state': task.state,
            'result': result['image_url']
        }
    else:
        response = {
            'state': task.state,
            'result': str(task.info),
        }
    print("response", response, flush=True)
    return jsonify(response)   




