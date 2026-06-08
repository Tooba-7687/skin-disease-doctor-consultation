# Celery Tasks for Async Processing (Optional - enables background Grad-CAM generation)
# To enable: 1) Install celery: pip install celery redis
#           2) Configure in settings.py: CELERY_BROKER_URL, CELERY_RESULT_BACKEND
#           3) Uncomment async calls in views.py

from celery import shared_task
from django.core.files import File
from django.conf import settings
from .models import Prediction
from .utils import generate_gradcam
import os

@shared_task(bind=True, max_retries=3)
def generate_gradcam_async(self, prediction_id):
    """
    Asynchronously generate Grad-CAM for a prediction
    Allows image analysis to return immediately to user
    """
    try:
        prediction = Prediction.objects.get(id=prediction_id)
        image_path = prediction.image.path
        gradcam_filename = f"gradcam_{prediction_id}.jpg"
        gradcam_path = os.path.join(
            settings.MEDIA_ROOT,
            'gradcam',
            gradcam_filename
        )
        
        os.makedirs(os.path.dirname(gradcam_path), exist_ok=True)
        
        # Generate Grad-CAM with fast mode
        generate_gradcam(image_path, gradcam_path, use_fast_mode=True)
        
        # Save to prediction if successful
        if os.path.exists(gradcam_path):
            with open(gradcam_path, 'rb') as f:
                prediction.gradcam_image.save(
                    gradcam_filename,
                    File(f),
                    save=True
                )
            print(f"✅ Async Grad-CAM completed for prediction {prediction_id}")
        else:
            print(f"⚠️ Async Grad-CAM file not created for prediction {prediction_id}")
            
    except Prediction.DoesNotExist:
        print(f"❌ Prediction {prediction_id} not found")
    except Exception as e:
        print(f"❌ Async Grad-CAM error: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60)
