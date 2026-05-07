from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files import File
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils import timezone
from .models import (
    UserProfile, DoctorProfile, DoctorEducation,
    DoctorCertification, DoctorWorkExperience,
    Prediction, Consultation, ConsultationMessage,
    Prescription, DoctorReview
)
from .forms import (
    PatientSignUpForm, DoctorSignUpForm, DoctorProfileForm,
    DoctorEducationForm, DoctorCertificationForm,
    DoctorWorkExperienceForm, ConsultationNoteForm,
    PrescriptionForm, DoctorReviewForm, ConsultationStatusForm
)
from .utils import predict_disease, generate_gradcam
import os


# ============================================
# HOME PAGE
# ============================================
def home(request):
    context = {}
    
    # Check if user is a patient with active consultations
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.role == 'patient':
                # Get patient's active consultations
                active_consultations = Consultation.objects.filter(
                    patient=request.user
                ).exclude(status='cancelled')
                
                context['active_consultations'] = active_consultations
                context['has_active_consultation'] = active_consultations.exists()
                
                if active_consultations.exists():
                    context['first_active_consultation'] = active_consultations.first()
        except UserProfile.DoesNotExist:
            pass
    
    return render(request, 'home.html', context)


# ============================================
# ROLE SELECTION
# ============================================
def role_selector(request):
    """Allow user to choose between patient and doctor signup/login"""
    return render(request, 'role_selector.html')


# ============================================
# PATIENT SIGNUP
# ============================================
def patient_signup_view(request):
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.role == 'patient':
                return redirect('upload')
            else:
                return redirect('doctor_dashboard')
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            UserProfile.objects.create(user=request.user, role='patient')
            return redirect('upload')

    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            first_name = form.cleaned_data.get('first_name', '')
            last_name = form.cleaned_data.get('last_name', '')
            phone_number = form.cleaned_data.get('phone_number', '')

            # Validations
            if password1 != password2:
                messages.error(request, 'Passwords do not match!')
                return render(request, 'patient_signup.html', {'form': form})

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken!')
                return render(request, 'patient_signup.html', {'form': form})

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered!')
                return render(request, 'patient_signup.html', {'form': form})

            if len(password1) < 6:
                messages.error(request, 'Password must be at least 6 characters!')
                return render(request, 'patient_signup.html', {'form': form})

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )

            # Create user profile
            UserProfile.objects.create(
                user=user,
                role='patient',
                phone_number=phone_number
            )

            login(request, user)
            messages.success(request, f'Welcome {username}! Account created successfully!')
            return redirect('upload')
    else:
        form = PatientSignUpForm()

    return render(request, 'patient_signup.html', {'form': form})


# ============================================
# DOCTOR SIGNUP
# ============================================
def doctor_signup_view(request):
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role == 'doctor':
            return redirect('doctor_complete_profile')
        else:
            return redirect('upload')

    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            # Validations
            if password1 != password2:
                messages.error(request, 'Passwords do not match!')
                return render(request, 'doctor_signup.html', {'form': form})

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken!')
                return render(request, 'doctor_signup.html', {'form': form})

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered!')
                return render(request, 'doctor_signup.html', {'form': form})

            if len(password1) < 6:
                messages.error(request, 'Password must be at least 6 characters!')
                return render(request, 'doctor_signup.html', {'form': form})

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )

            # Create user profile
            UserProfile.objects.create(
                user=user,
                role='doctor'
            )

            # Create doctor profile
            DoctorProfile.objects.create(
                user=user,
                medical_license_number='',
                specialization='',
                years_of_experience=0,
                profile_status='incomplete'
            )

            login(request, user)
            messages.success(request, 'Welcome! Please complete your professional profile.')
            return redirect('doctor_complete_profile')
    else:
        form = DoctorSignUpForm()

    return render(request, 'doctor_signup.html', {'form': form})


# ============================================
# LOGIN PAGE (UPDATED)
# ============================================
def login_view(request):
    if request.user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'role': 'patient'}
        )
        if user_profile.role == 'patient':
            return redirect('upload')
        else:
            return redirect('doctor_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role', 'patient')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Get or create user profile
            user_profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': role}
            )
            
            # Check if user role matches selected role
            if user_profile.role != role:
                messages.error(request, f'This account is registered as a {user_profile.get_role_display()}, not a {role}!')
                return render(request, 'login.html')

            login(request, user)
            messages.success(request, f'Welcome back {username}!')
            
            # Redirect based on role
            if user_profile.role == 'doctor':
                return redirect('doctor_dashboard')
            
            return redirect('upload')
        else:
            messages.error(request, 'Invalid username or password!')
            return render(request, 'login.html')

    return render(request, 'login.html')


# ============================================
# LOGOUT
# ============================================
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')


# ============================================
# PATIENT VIEWS
# ============================================

@login_required(login_url='login')
def upload(request):
    # Check if user is patient
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'patient':
            messages.error(request, 'Only patients can upload images.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        # Auto-create profile if missing
        user_profile = UserProfile.objects.create(user=request.user, role='patient')
        messages.info(request, 'Profile created automatically.')

    if request.method == 'POST':
        if 'image' not in request.FILES:
            messages.error(request, 'Please select an image!')
            return redirect('upload')

        img_file = request.FILES['image']

        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if img_file.content_type not in allowed_types:
            messages.error(request, 'Only JPG and PNG images are allowed!')
            return redirect('upload')

        # Validate file size (max 10MB)
        if img_file.size > 10 * 1024 * 1024:
            messages.error(request, 'Image size must be less than 10MB!')
            return redirect('upload')

        try:
            # Save image temporarily for prediction
            temp_filename = f"temp_{request.user.id}_{img_file.name}"
            temp_path = default_storage.save(f'uploads/{temp_filename}', img_file)
            full_temp_path = os.path.join(settings.MEDIA_ROOT, temp_path)

            # Run prediction on temp file
            result = predict_disease(full_temp_path)
            
            # Validate result
            if not result or not isinstance(result, dict):
                raise ValueError("Invalid prediction result returned")
            
            if 'confidence' not in result or result['confidence'] is None:
                raise ValueError("Confidence value is missing from prediction result")

            # Create prediction with all data
            prediction = Prediction()
            prediction.image = img_file
            prediction.user = request.user
            prediction.disease_code = result['disease_code']
            prediction.disease_name = result['disease_name']
            prediction.confidence = result['confidence']
            prediction.severity = result['severity']
            prediction.description = result['description']
            prediction.care_suggestion = result['care_suggestion']
            prediction.save()

            # Generate Grad-CAM using the saved image path (optimized for speed)
            try:
                image_path = prediction.image.path
                gradcam_filename = f"gradcam_{prediction.id}.jpg"
                gradcam_path = os.path.join(
                    settings.MEDIA_ROOT,
                    'gradcam',
                    gradcam_filename
                )
                os.makedirs(os.path.dirname(gradcam_path), exist_ok=True)
                
                # Generate Grad-CAM with fast mode enabled
                generate_gradcam(image_path, gradcam_path, use_fast_mode=True)
                
                # Verify file was created
                if os.path.exists(gradcam_path):
                    # Save gradcam_image using relative path
                    with open(gradcam_path, 'rb') as f:
                        prediction.gradcam_image.save(
                            gradcam_filename,
                            File(f),
                            save=True
                        )
                    print(f"✅ Grad-CAM file saved: {gradcam_filename}")
                    messages.success(request, 'AI visualization generated successfully!')
                else:
                    print("❌ Grad-CAM file was not created")
                    messages.warning(request, 'AI visualization could not be generated.')
            except Exception as e:
                print(f"❌ Error generating Grad-CAM: {str(e)}")
                messages.warning(request, 'AI visualization generation failed.')

            # Clean up temp file
            if os.path.exists(full_temp_path):
                os.remove(full_temp_path)

            return redirect('result', pk=prediction.id)

        except Exception as e:
            messages.error(request, f'Error processing image: {str(e)}')
            return redirect('upload')

    return render(request, 'upload.html')


@login_required(login_url='login')
def result(request, pk):
    prediction = get_object_or_404(Prediction, pk=pk)

    severity_colors = {
        'Low': 'success',
        'Moderate': 'warning',
        'High': 'danger',
        'Very High': 'danger'
    }

    color = severity_colors.get(prediction.severity, 'info')
    
    # Get consultations for this prediction
    consultations = Consultation.objects.filter(prediction=prediction)
    
    # Check if user has any active/pending consultation for this prediction
    has_consultation = consultations.filter(
        patient=request.user
    ).exclude(status='cancelled').exists()
    
    # Get the consultation if it exists for showing in template
    active_consultation = consultations.filter(
        patient=request.user
    ).exclude(status='cancelled').first()
    
    context = {
        'prediction': prediction,
        'severity_color': color,
        'consultations': consultations,
        'has_consultation': has_consultation,
        'active_consultation': active_consultation,
    }
    return render(request, 'result.html', context)


@login_required(login_url='login')
def history(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'patient':
            messages.error(request, 'Only patients can view history.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        pass

    predictions = Prediction.objects.filter(user=request.user)
    context = {'predictions': predictions}
    return render(request, 'history.html', context)


@login_required(login_url='login')
def delete_prediction(request, pk):
    prediction = get_object_or_404(Prediction, pk=pk, user=request.user)

    if prediction.image:
        if os.path.exists(prediction.image.path):
            os.remove(prediction.image.path)

    if prediction.gradcam_image:
        gradcam_path = os.path.join(settings.MEDIA_ROOT, str(prediction.gradcam_image))
        if os.path.exists(gradcam_path):
            os.remove(gradcam_path)

    prediction.delete()
    messages.success(request, 'Record deleted successfully!')
    return redirect('history')


@login_required(login_url='login')
def download_result(request, pk):
    prediction = get_object_or_404(Prediction, pk=pk)

    report = f"""
SKIN DISEASE DETECTION REPORT
==============================
Patient        : {prediction.user.username}
Date           : {prediction.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Disease Name   : {prediction.disease_name}
Confidence     : {prediction.confidence}%
Severity       : {prediction.severity}
Description    : {prediction.description}
Care Suggestion: {prediction.care_suggestion}
==============================
DISCLAIMER: This is not a medical diagnosis.
Please consult a dermatologist for proper treatment.
    """

    response = HttpResponse(report, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="skin_report_{pk}.txt"'
    return response


# ============================================
# DOCTOR VIEWS
# ============================================

@login_required(login_url='login')
def doctor_complete_profile(request):
    """Doctor completes their professional profile"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'doctor':
            messages.error(request, 'Only doctors can access this page.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)

    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=doctor_profile)
        if form.is_valid():
            doctor_profile = form.save(commit=False)
            doctor_profile.profile_status = 'pending_approval'
            doctor_profile.save()
            messages.success(request, 'Professional information saved. Your profile is now pending admin verification.')
            return redirect('doctor_profile_status')
    else:
        form = DoctorProfileForm(instance=doctor_profile)

    context = {
        'form': form,
        'doctor_profile': doctor_profile,
    }
    return render(request, 'doctor_profile_form.html', context)


@login_required(login_url='login')
def doctor_profile_status(request):
    """Check doctor profile verification status"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'doctor':
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')

    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    
    context = {
        'doctor_profile': doctor_profile,
    }
    return render(request, 'doctor_profile_status.html', context)


@login_required(login_url='login')
def doctor_add_education(request):
    """Add education to doctor profile"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'doctor':
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')

    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)

    if request.method == 'POST':
        form = DoctorEducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.doctor = doctor_profile
            education.save()
            messages.success(request, 'Education added successfully.')
            return redirect('doctor_complete_profile')
    else:
        form = DoctorEducationForm()

    context = {
        'form': form,
        'title': 'Add Education',
    }
    return render(request, 'doctor_education_form.html', context)


@login_required(login_url='login')
def doctor_add_certification(request):
    """Add certification to doctor profile"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'doctor':
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')

    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)

    if request.method == 'POST':
        form = DoctorCertificationForm(request.POST, request.FILES)
        if form.is_valid():
            certification = form.save(commit=False)
            certification.doctor = doctor_profile
            certification.save()
            messages.success(request, 'Certification added successfully.')
            return redirect('doctor_complete_profile')
    else:
        form = DoctorCertificationForm()

    context = {
        'form': form,
        'title': 'Add Certification',
    }
    return render(request, 'doctor_certification_form.html', context)


@login_required(login_url='login')
def doctor_add_work_experience(request):
    """Add work experience to doctor profile"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'doctor':
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')

    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)

    if request.method == 'POST':
        form = DoctorWorkExperienceForm(request.POST)
        if form.is_valid():
            work_exp = form.save(commit=False)
            work_exp.doctor = doctor_profile
            work_exp.save()
            messages.success(request, 'Work experience added successfully.')
            return redirect('doctor_complete_profile')
    else:
        form = DoctorWorkExperienceForm()

    context = {
        'form': form,
        'title': 'Add Work Experience',
    }
    return render(request, 'doctor_work_experience_form.html', context)


@login_required(login_url='login')
def doctor_dashboard(request):
    """Doctor dashboard"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'doctor':
            messages.error(request, 'Only doctors can access this page.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)

    # Check if profile is approved
    if not doctor_profile.is_admin_verified:
        messages.warning(request, 'Your profile is pending admin verification. You will have full access once approved.')

    # Get pending consultations for this doctor
    pending_consultations = Consultation.objects.filter(
        doctor=request.user,
        status='pending'
    )

    # Get doctor's consultations
    my_consultations = Consultation.objects.filter(doctor=request.user)
    in_progress = my_consultations.filter(status='in_progress')
    completed = my_consultations.filter(status='completed')

    context = {
        'doctor_profile': doctor_profile,
        'pending_consultations': pending_consultations,
        'in_progress_consultations': in_progress,
        'completed_consultations': completed,
    }
    return render(request, 'doctor_dashboard.html', context)


@login_required(login_url='login')
def consultation_list(request):
    """List all consultations for doctor"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'doctor':
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')

    consultations = Consultation.objects.filter(doctor=request.user)

    context = {
        'consultations': consultations,
    }
    return render(request, 'consultation_list.html', context)


@login_required(login_url='login')
def consultation_detail(request, pk):
    """View consultation details and chat"""
    consultation = get_object_or_404(Consultation, pk=pk)

    # Check permissions
    if request.user != consultation.patient and request.user != consultation.doctor:
        messages.error(request, 'You do not have permission to view this consultation.')
        return redirect('home')

    # Check if doctor is verified
    if request.user == consultation.doctor:
        doctor_profile = consultation.doctor.doctor_profile
        if not doctor_profile.is_admin_verified and consultation.status == 'pending':
            messages.warning(request, 'You cannot accept consultations until your profile is verified.')

    if request.method == 'POST':
        # Accept consultation (doctor only)
        if 'accept_consultation' in request.POST and request.user == consultation.doctor:
            doctor_profile = consultation.doctor.doctor_profile
            if doctor_profile.is_admin_verified:
                consultation.status = 'in_progress'
                consultation.save()
                messages.success(request, 'Consultation accepted.')
                return redirect('consultation_detail', pk=pk)
            else:
                messages.error(request, 'Your profile must be verified before accepting consultations.')

        # Complete consultation (doctor only)
        if 'complete_consultation' in request.POST and request.user == consultation.doctor:
            if consultation.status == 'in_progress':
                consultation.status = 'completed'
                consultation.save()
                messages.success(request, 'Consultation marked as completed.')
                return redirect('consultation_detail', pk=pk)
            else:
                messages.error(request, 'Only in-progress consultations can be completed.')

        # Send message
        if 'message' in request.POST:
            message_text = request.POST.get('message', '').strip()
            if message_text:
                ConsultationMessage.objects.create(
                    consultation=consultation,
                    sender=request.user,
                    message=message_text
                )
                return redirect('consultation_detail', pk=pk)

    chat_messages = ConsultationMessage.objects.filter(consultation=consultation)
    
    context = {
        'consultation': consultation,
        'messages': chat_messages,
    }
    return render(request, 'consultation_detail.html', context)


@login_required(login_url='login')
def browse_doctors(request):
    """Patient browses available doctors"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'patient':
            return redirect('home')
    except UserProfile.DoesNotExist:
        pass

    # Get approved doctors
    doctors = DoctorProfile.objects.filter(is_admin_verified=True)

    # Filter by specialization if provided
    specialization = request.GET.get('specialization', '')
    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)

    # Add ratings and consultation status to each doctor object
    for doctor in doctors:
        reviews = DoctorReview.objects.filter(doctor=doctor)
        if reviews.exists():
            avg_rating = sum([r.rating for r in reviews]) / len(reviews)
            doctor.avg_rating = round(avg_rating, 1)
            doctor.review_count = len(reviews)
        else:
            doctor.avg_rating = None
            doctor.review_count = 0
        
        # Check if patient has active consultation with this doctor
        active_consultation = Consultation.objects.filter(
            patient=request.user,
            doctor=doctor.user
        ).exclude(status='cancelled').first()
        
        doctor.active_consultation = active_consultation
        doctor.has_consultation = active_consultation is not None

    context = {
        'doctors': doctors,
        'specialization_filter': specialization,
    }
    return render(request, 'browse_doctors.html', context)


@login_required(login_url='login')
def doctor_profile_view(request, doctor_id):
    """View doctor profile"""
    doctor_profile = get_object_or_404(DoctorProfile, id=doctor_id)

    # Get reviews
    reviews = DoctorReview.objects.filter(doctor=doctor_profile)
    avg_rating = None
    if reviews.exists():
        avg_rating = sum([r.rating for r in reviews]) / len(reviews)
    
    # Check if patient has active consultation with this doctor
    active_consultation = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.role == 'patient':
                active_consultation = Consultation.objects.filter(
                    patient=request.user,
                    doctor=doctor_profile.user
                ).exclude(status='cancelled').first()
        except UserProfile.DoesNotExist:
            pass

    context = {
        'doctor_profile': doctor_profile,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'active_consultation': active_consultation,
        'has_consultation': active_consultation is not None,
    }
    return render(request, 'doctor_profile_view.html', context)


@login_required(login_url='login')
def request_consultation(request, prediction_id, doctor_id):
    """Patient requests consultation with doctor"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'patient':
            messages.error(request, 'Only patients can request consultations.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        pass

    prediction = get_object_or_404(Prediction, id=prediction_id, user=request.user)
    doctor = get_object_or_404(User, id=doctor_id)

    # Check if patient already has ANY active consultation with this doctor
    existing = Consultation.objects.filter(
        patient=request.user,
        doctor=doctor
    ).exclude(status='cancelled').first()

    if existing:
        messages.warning(request, f'You already have an active consultation with Dr. {doctor.first_name} {doctor.last_name}.')
        return redirect('consultation_detail', pk=existing.id)

    # Create consultation
    consultation = Consultation.objects.create(
        patient=request.user,
        prediction=prediction,
        doctor=doctor,
        status='pending'
    )

    messages.success(request, 'Consultation request sent to doctor.')
    return redirect('consultation_detail', pk=consultation.id)


@login_required(login_url='login')
def quick_request_consultation(request, doctor_id):
    """Quick consultation request from doctor profile - uses latest prediction"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'patient':
            messages.error(request, 'Only patients can request consultations.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        pass

    # Get patient's latest prediction
    latest_prediction = Prediction.objects.filter(user=request.user).order_by('-created_at').first()
    
    if not latest_prediction:
        messages.warning(request, 'Please upload an image for diagnosis first before requesting a consultation.')
        return redirect('upload')
    
    # Try to get doctor by DoctorProfile ID first, fallback to User ID
    doctor = None
    try:
        doctor_profile = DoctorProfile.objects.get(id=doctor_id)
        doctor = doctor_profile.user
    except DoctorProfile.DoesNotExist:
        # Try to get doctor by User ID
        doctor = get_object_or_404(User, id=doctor_id)
        try:
            doctor_profile = doctor.doctor_profile
        except DoctorProfile.DoesNotExist:
            messages.error(request, 'This doctor profile does not exist.')
            return redirect('browse_doctors')
    
    # Check if patient already has ANY active consultation with this doctor
    existing = Consultation.objects.filter(
        patient=request.user,
        doctor=doctor
    ).exclude(status='cancelled').first()

    if existing:
        messages.info(request, f'You already have an active consultation with Dr. {doctor.first_name} {doctor.last_name}.')
        return redirect('consultation_detail', pk=existing.id)

    # Create consultation
    consultation = Consultation.objects.create(
        patient=request.user,
        prediction=latest_prediction,
        doctor=doctor,
        status='pending'
    )

    messages.success(request, f'Consultation request sent to Dr. {doctor.first_name} {doctor.last_name}.')
    return redirect('consultation_detail', pk=consultation.id)


@login_required(login_url='login')
def prescription_create(request, consultation_id):
    """Doctor creates prescription"""
    consultation = get_object_or_404(Consultation, id=consultation_id)

    # Check permissions
    if request.user != consultation.doctor:
        messages.error(request, 'Only the assigned doctor can create prescriptions.')
        return redirect('home')

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.consultation = consultation
            prescription.doctor = request.user
            prescription.patient = consultation.patient
            prescription.save()
            messages.success(request, 'Prescription created successfully.')
            return redirect('prescription_detail', pk=prescription.id)
    else:
        form = PrescriptionForm()

    context = {
        'form': form,
        'consultation': consultation,
    }
    return render(request, 'prescription_form.html', context)


@login_required(login_url='login')
def prescription_detail(request, pk):
    """View prescription"""
    prescription = get_object_or_404(Prescription, id=pk)

    # Check permissions
    if request.user != prescription.patient and request.user != prescription.doctor:
        messages.error(request, 'You do not have permission to view this prescription.')
        return redirect('home')

    context = {
        'prescription': prescription,
    }
    return render(request, 'prescription_detail.html', context)


@login_required(login_url='login')
def prescription_pdf(request, pk):
    """Download prescription as PDF"""
    prescription = get_object_or_404(Prescription, id=pk)

    # Check permissions
    if request.user != prescription.patient and request.user != prescription.doctor:
        messages.error(request, 'You do not have permission to download this prescription.')
        return redirect('home')

    report = f"""
MEDICAL PRESCRIPTION
==============================
Patient         : {prescription.patient.get_full_name() or prescription.patient.username}
Doctor          : Dr. {prescription.doctor.get_full_name() or prescription.doctor.username}
Date            : {prescription.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Consultation ID : {prescription.consultation.id}

==============================
PRESCRIPTION DETAILS
==============================
Medicine Name   : {prescription.medicine_name}
Dosage          : {prescription.dosage}
Frequency       : {prescription.frequency}
Duration        : {prescription.duration_days} days

Instructions    : {prescription.instructions or 'None'}
Side Effects    : {prescription.side_effects_warning or 'None'}

==============================
DISCLAIMER: Follow doctor's instructions for medication.
For any concerns, contact your doctor immediately.
    """

    response = HttpResponse(report, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="prescription_{pk}.txt"'
    return response


@login_required(login_url='login')
def add_doctor_review(request, doctor_id):
    """Patient adds review for doctor"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'patient':
            messages.error(request, 'Only patients can add reviews.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

    doctor_profile = get_object_or_404(DoctorProfile, id=doctor_id)

    # Check if patient has uploaded an image
    has_prediction = Prediction.objects.filter(user=request.user).exists()
    if not has_prediction:
        messages.error(request, 'You must upload an image for diagnosis before leaving a review.')
        return redirect('upload')

    # Check if patient has consulted with this doctor
    has_consultation = Consultation.objects.filter(
        patient=request.user,
        doctor=doctor_profile.user
    ).exclude(status='cancelled').exists()

    if not has_consultation:
        messages.error(request, 'You can only review doctors you have consulted with.')
        return redirect('browse_doctors')

    # Check if review already exists
    existing_review = DoctorReview.objects.filter(
        doctor=doctor_profile,
        patient=request.user
    ).exists()

    if existing_review:
        messages.warning(request, 'You have already reviewed this doctor.')
        return redirect('doctor_profile_view', doctor_id=doctor_id)

    if request.method == 'POST':
        form = DoctorReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.doctor = doctor_profile
            review.patient = request.user
            review.save()
            messages.success(request, 'Thank you for your review.')
            return redirect('doctor_profile_view', doctor_id=doctor_id)
    else:
        form = DoctorReviewForm()

    context = {
        'form': form,
        'doctor_profile': doctor_profile,
    }
    return render(request, 'doctor_review_form.html', context)


@login_required
def add_consultation_review(request, consultation_id):
    """Patient adds review for doctor from consultation page"""
    # Get the consultation
    consultation = get_object_or_404(Consultation, id=consultation_id)
    
    # Verify the user is the patient
    if consultation.patient != request.user:
        messages.error(request, 'You can only review your own consultations.')
        return redirect('home')
    
    # Verify consultation is completed
    if consultation.status != 'completed':
        messages.error(request, 'You can only review completed consultations.')
        return redirect('consultation_detail', consultation_id=consultation_id)
    
    # Verify doctor exists
    if not consultation.doctor:
        messages.error(request, 'This consultation does not have a doctor assigned.')
        return redirect('consultation_detail', consultation_id=consultation_id)
    
    # Try to get or create doctor profile
    doctor_profile, created = DoctorProfile.objects.get_or_create(user=consultation.doctor)
    
    # Check if review already exists
    existing_review = DoctorReview.objects.filter(
        doctor=doctor_profile,
        patient=request.user
    ).exists()

    if existing_review:
        messages.warning(request, 'You have already reviewed this doctor.')
        return redirect('consultation_detail', consultation_id=consultation_id)

    if request.method == 'POST':
        form = DoctorReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.doctor = doctor_profile
            review.patient = request.user
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('consultation_detail', consultation_id=consultation_id)
    else:
        form = DoctorReviewForm()

    context = {
        'form': form,
        'doctor_profile': doctor_profile,
        'consultation': consultation,
    }
    return render(request, 'doctor_review_form.html', context)