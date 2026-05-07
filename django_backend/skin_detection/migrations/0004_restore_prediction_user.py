# Generated migration to restore user field to Prediction model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('skin_detection', '0003_remove_prediction_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='prediction',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
