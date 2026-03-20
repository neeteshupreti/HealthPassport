from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.db.models import Q
from django.utils import timezone

from .models import (UserProfile, PatientProfile, HospitalProfile,
                     MedicalRecord, AccessRequest, Notification, Doctor, NepalLocation)
from .forms import (PatientRegistrationForm, HospitalRegistrationForm,
                    PatientProfileForm, HospitalProfileForm,
                    MedicalRecordForm, AccessRequestForm, PatientSearchForm,
                    HPassLookupForm, DoctorForm, AssignDoctorForm, AdminUserForm, ReportIssueForm)
from .decorators import patient_required, hospital_required, admin_required
from .utils import generate_patient_qr


# ─────────────────────────────────────────────
# PUBLIC VIEWS
# ─────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        # Ensure authenticated users can reach a dashboard
        if request.user.is_staff:
            return redirect('dashboard')
        if not hasattr(request.user, 'profile'):
            logout(request)
            messages.error(request, 'Your account is not fully configured. Please contact an admin.')
            return redirect('login')
        return redirect('dashboard')
    return render(request, 'core/home.html')


def register_choice(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Only admins can create user accounts. Please log in as an admin to proceed.')
        return redirect('login')
    return render(request, 'core/register_choice.html')


def register_patient(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Only admins can create patient accounts. Please log in as an admin.')
        return redirect('login')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            UserProfile.objects.create(
                user=user,
                role='patient',
                phone=form.cleaned_data.get('phone', '')
            )
            patient_profile = PatientProfile.objects.create(user=user)
            if form.cleaned_data.get('profile_photo'):
                patient_profile.profile_photo = form.cleaned_data['profile_photo']
                patient_profile.save()

            # Generate QR code
            try:
                generate_patient_qr(patient_profile, request)
            except Exception:
                pass  # QR generation is non-critical

            messages.success(request, f'Patient account created. HPass No: {patient_profile.hpass_number}')
            return redirect('admin_dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, 'core/register_patient.html', {'form': form})


def register_hospital(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Only admins can create hospital accounts. Please log in as an admin.')
        return redirect('login')

    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            UserProfile.objects.create(
                user=user,
                role='hospital',
                phone=form.cleaned_data.get('phone', '')
            )
            hospital_profile = HospitalProfile.objects.create(
                user=user,
                hospital_name=form.cleaned_data['hospital_name'],
                hospital_type=form.cleaned_data['hospital_type'],
                registration_number=form.cleaned_data.get('registration_number', ''),
                province=form.cleaned_data.get('province', ''),
                district=form.cleaned_data.get('district', ''),
                municipality=form.cleaned_data.get('municipality', ''),
                address=form.cleaned_data.get('address', ''),
            )
            if form.cleaned_data.get('logo'):
                hospital_profile.logo = form.cleaned_data['logo']
                hospital_profile.save()


            messages.success(request, 'Hospital account created! Awaiting verification by admin.')
            return redirect('admin_dashboard')
    else:
        form = HospitalRegistrationForm()
    return render(request, 'core/register_hospital.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            # Auto-create missing profile/patient for legacy or uninitialized users.
            if not user.is_staff:
                profile = getattr(user, 'profile', None)
                if not profile:
                    profile = UserProfile.objects.create(user=user, role='patient')
                if profile.role == 'patient' and not hasattr(user, 'patient_profile'):
                    patient_profile = PatientProfile.objects.create(user=user)
                    try:
                        generate_patient_qr(patient_profile, request)
                    except Exception:
                        pass

            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def dashboard(request):
    # Staff users should go straight to admin dashboard (no profile required)
    if request.user.is_staff:
        return redirect('admin_dashboard')

    profile = getattr(request.user, 'profile', None)
    if not profile:
        return redirect('home')

    if profile.role == 'patient':
        return redirect('patient_dashboard')
    elif profile.role == 'hospital':
        return redirect('hospital_dashboard')
    return redirect('home')


# ─────────────────────────────────────────────
# PATIENT VIEWS
# ─────────────────────────────────────────────

@patient_required
def patient_dashboard(request):
    patient = get_object_or_404(PatientProfile, user=request.user)

    # Ensure QR code exists (for legacy patients created before QR was enabled)
    if not patient.qr_code:
        try:
            generate_patient_qr(patient, request)
        except Exception:
            pass

    recent_records = patient.medical_records.all()[:5]
    timeline_records = patient.medical_records.all().order_by('-record_date')[:10]
    approved_hospitals = patient.access_requests.filter(status='approved')
    unread_notifications = request.user.notifications.filter(is_read=False)[:5]

    context = {
        'patient': patient,
        'recent_records': recent_records,
        'timeline_records': timeline_records,
        'approved_hospitals': approved_hospitals,
        'unread_notifications': unread_notifications,
        'total_records': patient.medical_records.count(),
    }
    return render(request, 'patient/dashboard.html', context)


@patient_required
def patient_profile_edit(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('patient_dashboard')
    else:
        form = PatientProfileForm(instance=patient)

    return render(request, 'patient/profile_edit.html', {
        'form': form,
        'patient': patient,
    })


@patient_required
def patient_records(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    records = patient.medical_records.all()

    record_type = request.GET.get('type', '')
    if record_type:
        records = records.filter(record_type=record_type)

    context = {
        'patient': patient,
        'records': records,
        'record_types': MedicalRecord.RECORD_TYPE_CHOICES,
        'selected_type': record_type,
    }
    return render(request, 'patient/records.html', context)


@patient_required
def patient_timeline(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    records = patient.medical_records.all().order_by('-record_date')
    return render(request, 'patient/timeline.html', {'patient': patient, 'records': records})


@patient_required
def patient_report_issue(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    approved_hospitals = patient.access_requests.filter(status='approved').select_related('hospital')

    if request.method == 'POST':
        form = ReportIssueForm(request.POST, hospitals=[ar.hospital for ar in approved_hospitals])
        if form.is_valid():
            hospital_id = form.cleaned_data.get('hospital')
            message = form.cleaned_data['message'].strip()

            recipients = []
            if hospital_id:
                try:
                    hospital = HospitalProfile.objects.get(id=int(hospital_id))
                    recipients.append(hospital.user)
                except HospitalProfile.DoesNotExist:
                    pass

            if not recipients:
                recipients = list(User.objects.filter(is_staff=True))

            for recipient in recipients:
                Notification.objects.create(
                    recipient=recipient,
                    notif_type='system',
                    title=f'Issue reported by {request.user.get_full_name() or request.user.username}',
                    message=message,
                )

            messages.success(request, 'Your report has been sent. Thank you.')
            return redirect('patient_dashboard')
    else:
        form = ReportIssueForm(hospitals=[ar.hospital for ar in approved_hospitals])

    return render(request, 'patient/report_issue.html', {'form': form, 'patient': patient})


@patient_required
def patient_access_requests(request):
    # Patient access request management is no longer allowed.
    messages.info(request, 'Hospital access is managed by hospitals. Please contact your provider if you need changes.')
    return redirect('patient_dashboard')


@patient_required
def respond_access_request(request, request_id, action):
    # Disabled: patients cannot approve/reject/revoke hospital access.
    messages.error(request, 'You do not have permission to change access requests.')
    return redirect('patient_dashboard')


@hospital_required
def hospital_link_patient(request, patient_id):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    patient = get_object_or_404(PatientProfile, id=patient_id)

    access, created = AccessRequest.objects.get_or_create(
        hospital=hospital, patient=patient,
        defaults={'status': 'approved'}
    )
    if not created and access.status != 'approved':
        access.status = 'approved'
        access.save()

    Notification.objects.create(
        recipient=patient.user,
        notif_type='access_approved',
        title='Hospital Linked',
        message=f'{hospital.hospital_name} can now upload records to your account.',
        link='/patient/records/'
    )

    messages.success(request, f'{patient.user.get_full_name() or patient.user.username} is now linked.')
    return redirect('hospital_search_patient')


@hospital_required
def hospital_unlink_patient(request, patient_id):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    patient = get_object_or_404(PatientProfile, id=patient_id)

    access = AccessRequest.objects.filter(hospital=hospital, patient=patient).first()
    if access:
        access.revoke()
        Notification.objects.create(
            recipient=patient.user,
            notif_type='access_revoked',
            title='Hospital Unlinked',
            message=f'{hospital.hospital_name} no longer has access to your records.',
        )
        messages.success(request, f'{patient.user.get_full_name() or patient.user.username} has been unlinked.')
    else:
        messages.info(request, 'This patient was not linked.')

    return redirect('hospital_search_patient')


@patient_required
def download_record(request, record_id):
    patient = get_object_or_404(PatientProfile, user=request.user)
    record = get_object_or_404(MedicalRecord, id=record_id, patient=patient)

    if not record.file:
        messages.error(request, 'No file is available for this record.')
        return redirect('patient_records')

    import os
    with open(record.file.path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        filename = os.path.basename(record.file.name)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


@patient_required
def regenerate_qr(request):
    # Prevent patients from regenerating QR codes via frontend.
    messages.info(request, 'QR regeneration is disabled. Contact support if you need a new QR.')
    return redirect('patient_dashboard')


# ─────────────────────────────────────────────
# HOSPITAL VIEWS
# ─────────────────────────────────────────────

@hospital_required
def hospital_dashboard(request):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    approved_patients = AccessRequest.objects.filter(hospital=hospital, status='approved')
    pending_sent = AccessRequest.objects.filter(hospital=hospital, status='pending')
    recent_uploads = MedicalRecord.objects.filter(uploaded_by=hospital).order_by('-uploaded_at')[:5]
    unread_notifications = request.user.notifications.filter(is_read=False)[:5]

    context = {
        'hospital': hospital,
        'approved_patients': approved_patients,
        'pending_sent': pending_sent,
        'recent_uploads': recent_uploads,
        'unread_notifications': unread_notifications,
        'total_uploads': MedicalRecord.objects.filter(uploaded_by=hospital).count(),
    }
    return render(request, 'hospital/dashboard.html', context)


@hospital_required
def hospital_profile_edit(request):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    if request.method == 'POST':
        form = HospitalProfileForm(request.POST, request.FILES, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hospital profile updated.')
            return redirect('hospital_dashboard')
    else:
        form = HospitalProfileForm(instance=hospital)
    return render(request, 'hospital/profile_edit.html', {'form': form, 'hospital': hospital})


@hospital_required
def hospital_search_patient(request):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    patients = []
    form = PatientSearchForm(request.GET or None)
    searched = False

    if form.is_valid():
        searched = True
        health_id = form.cleaned_data.get('health_id', '').strip()
        name = form.cleaned_data.get('name', '').strip()

        qs = PatientProfile.objects.all()
        if health_id:
            qs = qs.filter(health_id__icontains=health_id)
        elif name:
            qs = qs.filter(
                Q(user__first_name__icontains=name) |
                Q(user__last_name__icontains=name)
            )
        else:
            qs = PatientProfile.objects.none()

        # Attach access status (approved-only)
        for p in qs:
            ar = AccessRequest.objects.filter(hospital=hospital, patient=p, status='approved').first()
            p.access_status = 'approved' if ar else None
        patients = list(qs)

    return render(request, 'hospital/search_patient.html', {
        'form': form,
        'patients': patients,
        'searched': searched,
        'hospital': hospital,
    })


@hospital_required
def hospital_request_access(request, patient_id):
    # Deprecated: hospitals now link patients directly from the search page.
    messages.info(request, 'Link patients via the search page instead of sending access requests.')
    return redirect('hospital_search_patient')


@hospital_required
def hospital_patients(request):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    approved = AccessRequest.objects.filter(hospital=hospital, status='approved').select_related('patient__user')
    
    # Search and filter functionality
    search_query = request.GET.get('q', '').strip()
    blood_filter = request.GET.get('blood', '').strip()
    gender_filter = request.GET.get('gender', '').strip()
    
    if search_query:
        approved = approved.filter(
            Q(patient__user__first_name__icontains=search_query) |
            Q(patient__user__last_name__icontains=search_query) |
            Q(patient__user__email__icontains=search_query) |
            Q(patient__hpass_number__icontains=search_query)
        )
    
    if blood_filter:
        approved = approved.filter(patient__blood_group=blood_filter)
    
    if gender_filter:
        approved = approved.filter(patient__gender=gender_filter)
    
    # Get unique values for filter dropdowns
    all_approved = AccessRequest.objects.filter(hospital=hospital, status='approved').select_related('patient__user')
    blood_groups = sorted(set(ap.patient.blood_group for ap in all_approved if ap.patient.blood_group))
    genders = PatientProfile.objects.values_list('gender', flat=True).distinct()
    
    return render(request, 'hospital/patients.html', {
        'hospital': hospital, 
        'approved': approved,
        'search_query': search_query,
        'blood_filter': blood_filter,
        'gender_filter': gender_filter,
        'blood_groups': blood_groups,
        'genders': genders,
    })


@hospital_required
def hospital_upload_record(request, patient_id):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    patient = get_object_or_404(PatientProfile, id=patient_id)

    # Verify access
    access = AccessRequest.objects.filter(
        hospital=hospital, patient=patient, status='approved'
    ).first()
    if not access:
        messages.error(request, 'You do not have approved access to this patient.')
        return redirect('hospital_patients')

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, hospital=hospital)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.uploaded_by = hospital
            record.is_verified = True
            record.verified_at = timezone.now()
            record.save()

            Notification.objects.create(
                recipient=patient.user,
                notif_type='record_uploaded',
                title='New Medical Record',
                message=f'{hospital.hospital_name} uploaded a {record.get_record_type_display()}: {record.title}',
                link='/patient/records/'
            )
            messages.success(request, f'Record "{record.title}" uploaded and verified.')
            return redirect('hospital_patient_records', patient_id=patient.id)
    else:
        form = MedicalRecordForm(hospital=hospital)

    return render(request, 'hospital/upload_record.html', {
        'form': form, 'patient': patient, 'hospital': hospital
    })


@hospital_required
def hospital_patient_records(request, patient_id):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    patient = get_object_or_404(PatientProfile, id=patient_id)

    access = AccessRequest.objects.filter(
        hospital=hospital, patient=patient, status='approved'
    ).first()
    if not access:
        messages.error(request, 'You do not have access to this patient.')
        return redirect('hospital_patients')

    records = patient.medical_records.all()
    return render(request, 'hospital/patient_records.html', {
        'hospital': hospital, 'patient': patient, 'records': records
    })


# ─────────────────────────────────────────────
# EMERGENCY / PUBLIC VIEW
# ─────────────────────────────────────────────

def emergency_profile(request, health_id):
    patient = get_object_or_404(PatientProfile, health_id=health_id)
    return render(request, 'core/emergency_profile.html', {'patient': patient})


# ─────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────

@login_required
def notifications(request):
    notifs = request.user.notifications.all()
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', {'notifications': notifs})


# ─────────────────────────────────────────────
# ADMIN PANEL
# ─────────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    total_patients = PatientProfile.objects.count()
    total_hospitals = HospitalProfile.objects.count()
    verified_hospitals = HospitalProfile.objects.filter(is_verified=True).count()
    total_records = MedicalRecord.objects.count()
    pending_hospitals = HospitalProfile.objects.filter(is_verified=False)

    context = {
        'total_patients': total_patients,
        'total_hospitals': total_hospitals,
        'verified_hospitals': verified_hospitals,
        'total_records': total_records,
        'pending_hospitals': pending_hospitals,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    user_rows = []
    for u in users:
        try:
            profile = u.profile
        except Exception:
            profile = None
        user_rows.append({'user': u, 'profile': profile})
    return render(request, 'admin_panel/users.html', {'users': user_rows})


@admin_required
def admin_edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = getattr(user, 'profile', None)

    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=user, profile=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('admin_users')
    else:
        form = AdminUserForm(instance=user, profile=profile)

    return render(request, 'admin_panel/edit_user.html', {'form': form, 'user': user})


@admin_required
def admin_hospitals(request):
    q = request.GET.get('q', '').strip()
    province = request.GET.get('province', '').strip()
    district = request.GET.get('district', '').strip()

    hospitals = HospitalProfile.objects.select_related('user').order_by('hospital_name')
    if q:
        hospitals = hospitals.filter(
            Q(hospital_name__icontains=q) |
            Q(user__username__icontains=q) |
            Q(hospital_type__icontains=q) |
            Q(address__icontains=q)
        )
    if province:
        hospitals = hospitals.filter(province=province)
    if district:
        hospitals = hospitals.filter(district=district)

    return render(request, 'admin_panel/hospitals.html', {
        'hospitals': hospitals,
        'q': q,
        'province': province,
        'district': district,
        'provinces': NepalLocation.PROVINCE_CHOICES,
        'districts': NepalLocation.DISTRICT_CHOICES,
    })


@admin_required
def admin_edit_hospital(request, hospital_id):
    hospital = get_object_or_404(HospitalProfile, id=hospital_id)

    if request.method == 'POST':
        form = HospitalProfileForm(request.POST, request.FILES, instance=hospital)
        if form.is_valid():
            form.save()
            # Keep contact user details in sync
            hospital.user.first_name = request.POST.get('contact_first_name', hospital.user.first_name)
            hospital.user.last_name = request.POST.get('contact_last_name', hospital.user.last_name)
            hospital.user.email = request.POST.get('contact_email', hospital.user.email)
            requested_username = request.POST.get('contact_username', hospital.user.username).strip()
            if requested_username and requested_username != hospital.user.username:
                if not User.objects.filter(username=requested_username).exclude(id=hospital.user.id).exists():
                    hospital.user.username = requested_username
                else:
                    messages.error(request, f"Username '{requested_username}' is already taken.")
            hospital.user.save()

            messages.success(request, 'Hospital updated successfully.')
            return redirect('admin_hospitals')
    else:
        form = HospitalProfileForm(instance=hospital)

    return render(request, 'admin_panel/edit_hospital.html', {
        'form': form,
        'hospital': hospital,
    })


@login_required
def admin_verify_hospital(request, hospital_id):
    if not request.user.is_staff:
        return redirect('home')
    hospital = get_object_or_404(HospitalProfile, id=hospital_id)
    hospital.verify()
    Notification.objects.create(
        recipient=hospital.user,
        notif_type='system',
        title='Hospital Verified',
        message='Your hospital has been verified by the admin. You can now upload records.',
    )
    messages.success(request, f'{hospital.hospital_name} has been verified.')
    return redirect('admin_dashboard')


def scan_profile(request, identifier):
    """Public QR scan handler. Shows basic patient information and allows DOB to unlock records."""
    patient = PatientProfile.objects.filter(hpass_number__iexact=identifier).first()
    if not patient:
        try:
            patient = PatientProfile.objects.get(health_id=identifier)
        except PatientProfile.DoesNotExist:
            raise Http404('Patient not found')

    form = HPassLookupForm(initial={'hpass_number': patient.hpass_number})
    form.fields['hpass_number'].widget.attrs.update({'readonly': 'readonly'})
    records = None

    if request.method == 'POST':
        form = HPassLookupForm(request.POST)
        if form.is_valid():
            hpass_number = form.cleaned_data['hpass_number'].strip().upper()
            dob = form.cleaned_data['date_of_birth']
            if (hpass_number == (patient.hpass_number or '').upper() and
                    patient.date_of_birth == dob):
                records = patient.medical_records.all().order_by('-record_date')
            else:
                messages.error(request, 'HPass number and date of birth did not match.')

    return render(request, 'core/scan_profile.html', {
        'patient': patient,
        'form': form,
        'records': records,
    })


def lookup_records(request):
    """Public record lookup by HPass number and DOB."""
    form = HPassLookupForm(request.POST or None)
    patient = None
    records = None

    if request.method == 'POST' and form.is_valid():
        hpass_number = form.cleaned_data['hpass_number'].strip().upper()
        dob = form.cleaned_data['date_of_birth']
        try:
            patient = PatientProfile.objects.get(hpass_number__iexact=hpass_number)
        except PatientProfile.DoesNotExist:
            patient = None

        if patient and patient.date_of_birth == dob:
            records = patient.medical_records.all().order_by('-record_date')
        else:
            messages.error(request, 'No matching records found for the provided HPass and DOB.')

    return render(request, 'core/lookup_records.html', {
        'form': form,
        'patient': patient,
        'records': records,
    })


def qr_scanner(request):
    """Page that opens the device camera and scans a QR code to show patient info."""
    return render(request, 'core/qr_scanner.html')


@hospital_required
def hospital_doctors(request):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    doctors = hospital.doctors.all().order_by('name')
    
    # Search and filter functionality
    search_query = request.GET.get('q', '').strip()
    specialization_filter = request.GET.get('specialization', '').strip()
    
    if search_query:
        doctors = doctors.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(nmc_number__icontains=search_query)
        )
    
    if specialization_filter:
        doctors = doctors.filter(specialization=specialization_filter)
    
    # Get unique specializations for filter dropdown
    all_doctors = hospital.doctors.all()
    specializations = sorted(set(d.specialization for d in all_doctors if d.specialization))
    
    return render(request, 'hospital/doctors.html', {
        'hospital': hospital,
        'doctors': doctors,
        'search_query': search_query,
        'specialization_filter': specialization_filter,
        'specializations': specializations,
    })


@hospital_required
def hospital_add_doctor(request):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    search_query = request.GET.get('q', '').strip()

    available_doctors = Doctor.objects.exclude(hospitals=hospital).order_by('name')
    if search_query:
        available_doctors = available_doctors.filter(
            Q(name__icontains=search_query) |
            Q(nmc_number__icontains=search_query) |
            Q(specialization__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if request.method == 'POST':
        form = AssignDoctorForm(request.POST, hospital=hospital, doctors=available_doctors)
        if form.is_valid():
            doctor = form.cleaned_data['doctor']
            doctor.hospitals.add(hospital)
            messages.success(request, f'Dr. {doctor.name} ({doctor.nmc_number or "N/A"}) was assigned to {hospital.hospital_name}.')
            return redirect('hospital_doctors')
    else:
        form = AssignDoctorForm(hospital=hospital, doctors=available_doctors)

    return render(request, 'hospital/add_doctor.html', {
        'hospital': hospital,
        'form': form,
        'assign_mode': True,
        'search_query': search_query,
        'available_count': available_doctors.count(),
    })


@hospital_required
def hospital_edit_doctor(request, doctor_id):
    messages.warning(request, 'Doctor profile editing is restricted to admins.')
    return redirect('hospital_doctors')


@hospital_required
def hospital_delete_doctor(request, doctor_id):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    doctor = get_object_or_404(Doctor, id=doctor_id, hospitals=hospital)
    doctor.hospitals.remove(hospital)
    messages.success(request, f'Dr. {doctor.name} has been unassigned from {hospital.hospital_name}.')
    return redirect('hospital_doctors')


@admin_required
def admin_doctors(request):
    q = request.GET.get('q', '').strip()
    hospital_filter = request.GET.get('hospital', '').strip()
    hospital_search = request.GET.get('hospital_search', '').strip()

    hospitals = HospitalProfile.objects.order_by('hospital_name')
    if hospital_search:
        hospitals = hospitals.filter(hospital_name__icontains=hospital_search)

    doctors = Doctor.objects.prefetch_related('hospitals').order_by('name')
    if q:
        doctors = doctors.filter(
            Q(name__icontains=q) |
            Q(nmc_number__icontains=q) |
            Q(specialization__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q) |
            Q(hospitals__hospital_name__icontains=q)
        )

    if hospital_filter.isdigit():
        doctors = doctors.filter(hospitals__id=int(hospital_filter))

    doctors = doctors.distinct()

    return render(request, 'admin_panel/doctors.html', {
        'doctors': doctors,
        'q': q,
        'hospitals': hospitals,
        'hospital_filter': hospital_filter,
        'hospital_search': hospital_search,
    })


@admin_required
def admin_add_doctor(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor added successfully.')
            return redirect('admin_doctors')
    else:
        form = DoctorForm()
    return render(request, 'admin_panel/edit_doctor.html', {
        'form': form,
        'is_new': True,
    })


@admin_required
def admin_edit_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor updated successfully.')
            return redirect('admin_doctors')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'admin_panel/edit_doctor.html', {
        'form': form,
        'doctor': doctor,
        'is_new': False,
    })


@admin_required
def admin_delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.delete()
    messages.success(request, 'Doctor deleted successfully.')
    return redirect('admin_doctors')


@admin_required
def admin_patients(request):
    q = request.GET.get('q', '').strip()
    province = request.GET.get('province', '').strip()
    district = request.GET.get('district', '').strip()

    patients = PatientProfile.objects.select_related('user').order_by('user__username')
    if q:
        patients = patients.filter(
            Q(user__username__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__email__icontains=q) |
            Q(hpass_number__icontains=q) |
            Q(health_id__icontains=q)
        )
    if province:
        patients = patients.filter(province=province)
    if district:
        patients = patients.filter(district=district)

    patients = patients.distinct()

    return render(request, 'admin_panel/patients.html', {
        'patients': patients,
        'q': q,
        'province': province,
        'district': district,
        'provinces': NepalLocation.PROVINCE_CHOICES,
        'districts': NepalLocation.DISTRICT_CHOICES,
    })


@admin_required
def admin_edit_patient(request, patient_id):
    patient = get_object_or_404(PatientProfile, id=patient_id)
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            patient.user.first_name = request.POST.get('first_name', patient.user.first_name)
            patient.user.last_name = request.POST.get('last_name', patient.user.last_name)
            patient.user.email = request.POST.get('email', patient.user.email)
            patient.user.save()
            messages.success(request, 'Patient updated successfully.')
            return redirect('admin_patients')
    else:
        form = PatientProfileForm(instance=patient)

    return render(request, 'admin_panel/edit_patient.html', {
        'form': form,
        'patient': patient,
    })


@admin_required
def admin_delete_patient(request, patient_id):
    patient = get_object_or_404(PatientProfile, id=patient_id)
    user = patient.user
    patient.delete()
    user.delete()
    messages.success(request, 'Patient deleted successfully.')
    return redirect('admin_patients')


def doctor_profile(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    total_records = doctor.records.count()
    patient_count = PatientProfile.objects.filter(medical_records__doctor=doctor).distinct().count()
    return render(request, 'core/doctor_profile.html', {
        'doctor': doctor,
        'total_records': total_records,
        'patient_count': patient_count,
    })





