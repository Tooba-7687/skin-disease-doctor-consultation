# Generated migration for Doctor side features

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('skin_detection', '0004_restore_prediction_user'),
    ]

    operations = [
        # UserProfile model
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('patient', 'Patient'), ('doctor', 'Doctor')], default='patient', max_length=10)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profile_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        
        # DoctorProfile model
        migrations.CreateModel(
            name='DoctorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medical_license_number', models.CharField(max_length=50, unique=True)),
                ('specialization', models.CharField(max_length=100)),
                ('years_of_experience', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('profile_status', models.CharField(choices=[('incomplete', 'Incomplete'), ('pending_approval', 'Pending Admin Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='incomplete', max_length=20)),
                ('bio', models.TextField(blank=True, null=True)),
                ('office_address', models.TextField(blank=True, null=True)),
                ('office_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('is_admin_verified', models.BooleanField(default=False)),
                ('verification_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        
        # DoctorEducation model
        migrations.CreateModel(
            name='DoctorEducation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('degree', models.CharField(max_length=50)),
                ('school_name', models.CharField(max_length=200)),
                ('graduation_year', models.IntegerField()),
                ('details', models.TextField(blank=True, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education', to='skin_detection.doctorprofile')),
            ],
            options={
                'verbose_name_plural': 'Doctor Education',
            },
        ),
        
        # DoctorCertification model
        migrations.CreateModel(
            name='DoctorCertification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certification_name', models.CharField(max_length=200)),
                ('issuing_organization', models.CharField(max_length=200)),
                ('issue_date', models.DateField()),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('certificate_file', models.FileField(blank=True, null=True, upload_to='certificates/')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certifications', to='skin_detection.doctorprofile')),
            ],
        ),
        
        # DoctorWorkExperience model
        migrations.CreateModel(
            name='DoctorWorkExperience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hospital_name', models.CharField(max_length=200)),
                ('department', models.CharField(max_length=100)),
                ('position', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_experience', to='skin_detection.doctorprofile')),
            ],
            options={
                'verbose_name_plural': 'Doctor Work Experience',
            },
        ),
        
        # Consultation model
        migrations.CreateModel(
            name='Consultation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('consultation_notes', models.TextField(blank=True, null=True)),
                ('appointment_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='consultations_as_doctor', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultations_as_patient', to=settings.AUTH_USER_MODEL)),
                ('prediction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultations', to='skin_detection.prediction')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        
        # ConsultationMessage model
        migrations.CreateModel(
            name='ConsultationMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('attachment', models.FileField(blank=True, null=True, upload_to='consultation_attachments/')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('consultation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='skin_detection.consultation')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
        
        # Prescription model
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicine_name', models.CharField(max_length=200)),
                ('dosage', models.CharField(max_length=100)),
                ('frequency', models.CharField(max_length=100)),
                ('duration_days', models.IntegerField()),
                ('instructions', models.TextField(blank=True, null=True)),
                ('side_effects_warning', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('consultation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='skin_detection.consultation')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions_created', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions_received', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        
        # DoctorReview model
        migrations.CreateModel(
            name='DoctorReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('review_text', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='skin_detection.doctorprofile')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('doctor', 'patient')},
            },
        ),
    ]
