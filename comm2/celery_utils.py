from flask import Flask 
from flask import request
from werkzeug.utils import secure_filename
from celery import Celery


# Link celery with flask
def make_celery(app):
    """connect Flask app with Celery"""
    celery = Celery(app.import_name)
    celery.conf.update(app.config["CELERY_CONFIG"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery()