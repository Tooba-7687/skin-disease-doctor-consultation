# celery.py - Optional async task processing configuration
# Place this file in: django_backend/skin_disease_backend/celery.py

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skin_disease_backend.settings')

app = Celery('skin_disease_backend')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks
app.autodiscover_tasks()

# Optional: Configure task settings
app.conf.update(
    # Task configuration
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Karachi',
    enable_utc=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    
    # Task routing
    task_routes={
        'skin_detection.tasks.generate_gradcam_async': {'queue': 'default'},
    },
    
    # Task rate limits (optional)
    task_default_rate_limit='100/m',  # Max 100 tasks per minute
)

# Debug task (for testing)
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
