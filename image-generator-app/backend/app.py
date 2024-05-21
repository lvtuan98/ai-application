from flask import Flask
from routes.image_routes import image_bp
from celery import Celery
from config import Config
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:5001", "http://localhost:3000"])

    app.config.from_object(Config)

    app.register_blueprint(image_bp, url_prefix='/api/images')

    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    celery.autodiscover_tasks(['tasks'])
    return celery

app = create_app()
celery_app = make_celery(app)
