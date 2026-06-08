from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# ============================================
# USER ROLES AND PROFILES
# ============================================
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='patient'
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


# ============================================
# DOCTOR PROFILE MODELS
# ============================================
class DoctorProfile(models.Model):
    STATUS_CHOICES = [
        ('incomplete', 'Incomplete'),
        ('pending_approval', 'Pending Admin Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    medical_license_number = models.CharField(
        max_length=50,
        unique=True
    )
    specialization = models.CharField(max_length=100)
    years_of_experience = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    profile_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='incomplete'
    )
    bio = models.TextField(blank=True, null=True)
    office_address = models.TextField(blank=True, null=True)
    office_phone = models.CharField(max_length=20, blank=True, null=True)
    is_admin_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} - {self.specialization}"

    class Meta:
        ordering = ['-created_at']


class DoctorEducation(models.Model):
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='education'
    )
    degree = models.CharField(max_length=50)
    school_name = models.CharField(max_length=200)
    graduation_year = models.IntegerField()
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.degree} from {self.school_name} ({self.graduation_year})"

    class Meta:
        verbose_name_plural = "Doctor Education"


class DoctorCertification(models.Model):
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='certifications'
    )
    certification_name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    certificate_file = models.FileField(
        upload_to='certificates/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.certification_name} from {self.issuing_organization}"


class DoctorWorkExperience(models.Model):
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='work_experience'
    )
    hospital_name = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.position} at {self.hospital_name}"

    class Meta:
        verbose_name_plural = "Doctor Work Experience"


# ============================================
# PREDICTION MODEL (EXISTING - KEPT SAME)
# ============================================
class Prediction(models.Model):
    # User
    user            = models.ForeignKey(
        User,
        on_delete    = models.CASCADE,
        null         = True,
        blank        = True
    )

    # Image
    image           = models.ImageField(upload_to='uploads/')

    # Prediction Results
    disease_code    = models.CharField(max_length=10)
    disease_name    = models.CharField(max_length=100)
    confidence      = models.FloatField()
    severity        = models.CharField(max_length=20)
    description     = models.TextField()
    care_suggestion = models.TextField()

    # Grad-CAM
    gradcam_image   = models.ImageField(
        upload_to='gradcam/',
        null=True,
        blank=True
    )

    # Metadata
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.disease_name} - {self.confidence:.2f}% - {self.created_at}"


# ============================================
# CONSULTATION MODELS
# ============================================
class Consultation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consultations_as_patient'
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consultations_as_doctor',
        blank=True,
        null=True
    )
    prediction = models.ForeignKey(
        Prediction,
        on_delete=models.CASCADE,
        related_name='consultations'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    consultation_notes = models.TextField(blank=True, null=True)
    appointment_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Consultation - {self.patient.username} with Dr. {self.doctor.username if self.doctor else 'Unassigned'}"

    class Meta:
        ordering = ['-created_at']


class ConsultationMessage(models.Model):
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    message = models.TextField()
    attachment = models.FileField(
        upload_to='consultation_attachments/',
        blank=True,
        null=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} on {self.timestamp}"

    class Meta:
        ordering = ['timestamp']


# ============================================
# PRESCRIPTION MODEL
# ============================================
class Prescription(models.Model):
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='prescriptions_created'
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='prescriptions_received'
    )
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration_days = models.IntegerField()
    instructions = models.TextField(blank=True, null=True)
    side_effects_warning = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription - {self.medicine_name} for {self.patient.username}"

    class Meta:
        ordering = ['-created_at']


# ============================================
# DOCTOR REVIEW MODEL
# ============================================
class DoctorReview(models.Model):
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}/5 Review for Dr. {self.doctor.user.first_name} by {self.patient.username}"

    def get_rating_range(self):
        """Return range of stars for template display"""
        return range(self.rating)

    def get_empty_rating_range(self):
        """Return remaining stars for template display"""
        return range(5 - self.rating)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['doctor', 'patient']
