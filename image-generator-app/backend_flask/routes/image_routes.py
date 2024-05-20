from flask import Blueprint, request, jsonify
from tasks.image_tasks import generate_image_task

image_bp = Blueprint('image_bp', __name__)

@image_bp.route('/generate', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        task = generate_image_task.apply_async(args=[data])
        return jsonify({"task_id": task.id}), 202
    except Exception as e:
        return {"error": str(e)}, 500

@image_bp.route('/status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = generate_image_task.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        return jsonify({"status": task.state, "result": task.result}), 200
    else:
        return jsonify({"status": task.state}), 200
