import os
from flask import Flask
from celery import Celery
from flask_cors import CORS
from routes.image_routes import image_bp
from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, origins="*")

    app.register_blueprint(image_bp, url_prefix='/api/images')
    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=os.environ.get("CELERY_RESULT_BACKEND"),
        broker=os.environ.get("CELERY_BROKER_URL")
    )
    celery.conf.update(app.config)
    celery.autodiscover_tasks(['tasks'])
    return celery

app = create_app()
celery_app = make_celery(app)