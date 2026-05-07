from django.contrib import admin
from .models import (
    UserProfile, DoctorProfile, DoctorEducation,
    DoctorCertification, DoctorWorkExperience,
    Prediction, Consultation, ConsultationMessage,
    Prescription, DoctorReview
)

# ============================================
# USER PROFILE ADMIN
# ============================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone_number', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


# ============================================
# DOCTOR PROFILE ADMIN
# ============================================
class DoctorEducationInline(admin.TabularInline):
    model = DoctorEducation
    extra = 1


class DoctorCertificationInline(admin.TabularInline):
    model = DoctorCertification
    extra = 1


class DoctorWorkExperienceInline(admin.TabularInline):
    model = DoctorWorkExperience
    extra = 1


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'specialization',
        'years_of_experience',
        'profile_status',
        'is_admin_verified',
        'created_at'
    ]
    list_filter = [
        'profile_status',
        'is_admin_verified',
        'specialization',
        'created_at'
    ]
    search_fields = [
        'user__username',
        'user__email',
        'medical_license_number',
        'specialization'
    ]
    readonly_fields = ['created_at', 'updated_at', 'verification_date']
    inlines = [
        DoctorEducationInline,
        DoctorCertificationInline,
        DoctorWorkExperienceInline
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Professional Information', {
            'fields': (
                'medical_license_number',
                'specialization',
                'years_of_experience',
                'bio'
            )
        }),
        ('Contact Information', {
            'fields': ('office_address', 'office_phone')
        }),
        ('Verification Status', {
            'fields': (
                'profile_status',
                'is_admin_verified',
                'verification_date'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    ordering = ['-created_at']

    actions = ['approve_doctor', 'reject_doctor']

    def approve_doctor(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            is_admin_verified=True,
            profile_status='approved',
            verification_date=timezone.now()
        )
        self.message_user(request, f'{count} doctor(s) approved successfully.')
    approve_doctor.short_description = 'Approve selected doctors'

    def reject_doctor(self, request, queryset):
        count = queryset.update(profile_status='rejected')
        self.message_user(request, f'{count} doctor(s) rejected.')
    reject_doctor.short_description = 'Reject selected doctors'


@admin.register(DoctorEducation)
class DoctorEducationAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'degree', 'school_name', 'graduation_year']
    list_filter = ['graduation_year', 'degree']
    search_fields = ['doctor__user__username', 'school_name', 'degree']
    ordering = ['-graduation_year']


@admin.register(DoctorCertification)
class DoctorCertificationAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'certification_name', 'issuing_organization', 'issue_date']
    list_filter = ['issue_date', 'issuing_organization']
    search_fields = ['doctor__user__username', 'certification_name']
    ordering = ['-issue_date']


@admin.register(DoctorWorkExperience)
class DoctorWorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'hospital_name', 'position', 'department', 'start_date']
    list_filter = ['start_date', 'hospital_name', 'department']
    search_fields = ['doctor__user__username', 'hospital_name', 'position']
    ordering = ['-start_date']


# ============================================
# PREDICTION ADMIN (EXISTING)
# ============================================
@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'disease_name',
        'confidence',
        'severity',
        'created_at'
    ]
    list_filter = [
        'severity',
        'disease_name',
        'created_at'
    ]
    search_fields = [
        'disease_name',
        'disease_code'
    ]
    readonly_fields = [
        'created_at',
        'disease_code',
        'disease_name',
        'confidence',
        'severity',
        'description',
        'care_suggestion'
    ]
    ordering = ['-created_at']


# ============================================
# CONSULTATION ADMIN
# ============================================
class ConsultationMessageInline(admin.TabularInline):
    model = ConsultationMessage
    extra = 0
    readonly_fields = ['sender', 'timestamp']
    can_delete = False


class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'patient',
        'doctor',
        'prediction',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'patient__username',
        'doctor__username',
        'prediction__disease_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ConsultationMessageInline, PrescriptionInline]
    
    fieldsets = (
        ('Consultation Details', {
            'fields': ('patient', 'doctor', 'prediction', 'status')
        }),
        ('Appointment', {
            'fields': ('appointment_date',)
        }),
        ('Notes', {
            'fields': ('consultation_notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    ordering = ['-created_at']


@admin.register(ConsultationMessage)
class ConsultationMessageAdmin(admin.ModelAdmin):
    list_display = ['consultation', 'sender', 'timestamp', 'is_read']
    list_filter = ['timestamp', 'is_read']
    search_fields = ['consultation__id', 'sender__username', 'message']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']


# ============================================
# PRESCRIPTION ADMIN
# ============================================
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'patient',
        'doctor',
        'medicine_name',
        'dosage',
        'frequency',
        'created_at'
    ]
    list_filter = ['created_at', 'dosage']
    search_fields = [
        'patient__username',
        'doctor__username',
        'medicine_name'
    ]
    readonly_fields = ['created_at']
    ordering = ['-created_at']


# ============================================
# DOCTOR REVIEW ADMIN
# ============================================
@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'patient', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = [
        'doctor__user__username',
        'patient__username',
        'review_text'
    ]
    readonly_fields = ['created_at']
    ordering = ['-created_at']