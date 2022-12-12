
from flask_server import flask_server
from evaluator import HEAAN_Evaluator

# celery from CMD will invoke this instance of celery
celery_app = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery_app.conf.update(app.config)

tasks = celery_app.tasks.keys()
print(tasks)


app.autodiscover_tasks(['foo', bar'])