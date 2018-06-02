import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'filter.settings')
app = Celery('filter')

app.conf.beat_schedule = {
    'run-every-10-seconds': {
        'task': 'filter_app.tasks.test',
        'schedule': 10.0
    }
}

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()