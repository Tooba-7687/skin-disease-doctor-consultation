from django.urls import path
from . import views

urlpatterns = [
    # Home & Role Selection
    path('', views.home, name='home'),
    path('role-selector/', views.role_selector, name='role_selector'),

    # Patient Auth
    path('patient/signup/', views.patient_signup_view, name='patient_signup'),
    path('patient/login/', views.login_view, name='patient_login'),

    # Doctor Auth
    path('doctor/signup/', views.doctor_signup_view, name='doctor_signup'),
    path('doctor/login/', views.login_view, name='doctor_login'),

    # General Auth
    path('signin/', views.login_view, name='login'),
    path('signup/', views.patient_signup_view, name='signup'),
    path('signout/', views.logout_view, name='logout'),

    # Patient Pages
    path('upload/', views.upload, name='upload'),
    path('result/<int:pk>/', views.result, name='result'),
    path('history/', views.history, name='history'),
    path('delete/<int:pk>/', views.delete_prediction, name='delete_prediction'),
    path('download/<int:pk>/', views.download_result, name='download_result'),

    # Doctor Profile Management
    path('doctor/complete-profile/', views.doctor_complete_profile, name='doctor_complete_profile'),
    path('doctor/profile-status/', views.doctor_profile_status, name='doctor_profile_status'),
    path('doctor/add-education/', views.doctor_add_education, name='doctor_add_education'),
    path('doctor/add-certification/', views.doctor_add_certification, name='doctor_add_certification'),
    path('doctor/add-work-experience/', views.doctor_add_work_experience, name='doctor_add_work_experience'),

    # Doctor Dashboard & Views
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/consultations/', views.consultation_list, name='consultation_list'),
    path('doctor/profile/<int:doctor_id>/', views.doctor_profile_view, name='doctor_profile_view'),

    # Patient - Browse Doctors & Request Consultation
    path('browse-doctors/', views.browse_doctors, name='browse_doctors'),
    path('request-consultation/<int:prediction_id>/<int:doctor_id>/', views.request_consultation, name='request_consultation'),
    path('quick-consultation/<int:doctor_id>/', views.quick_request_consultation, name='quick_request_consultation'),

    # Consultation
    path('consultation/<int:pk>/', views.consultation_detail, name='consultation_detail'),

    # Prescription
    path('prescription/create/<int:consultation_id>/', views.prescription_create, name='prescription_create'),
    path('prescription/<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('prescription/<int:pk>/pdf/', views.prescription_pdf, name='prescription_pdf'),

    # Doctor Review
    path('doctor/<int:doctor_id>/review/', views.add_doctor_review, name='add_doctor_review'),
    path('consultation/<int:consultation_id>/review/', views.add_consultation_review, name='add_consultation_review'),
]

