import uuid
import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('hospital', 'Hospital'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_patient(self):
        return self.role == 'patient'

    @property
    def is_hospital(self):
        return self.role == 'hospital'


class NepalLocation:
    PROVINCE_CHOICES = [
        ('Province 1', 'Province 1'),
        ('Province 2', 'Province 2'),
        ('Bagmati Province', 'Bagmati Province'),
        ('Gandaki Province', 'Gandaki Province'),
        ('Lumbini Province', 'Lumbini Province'),
        ('Karnali Province', 'Karnali Province'),
        ('Sudurpashchim Province', 'Sudurpashchim Province'),
    ]

    DISTRICT_CHOICES = [
        ('Bhojpur','Bhojpur'), ('Dhankuta','Dhankuta'), ('Ilam','Ilam'), ('Jhapa','Jhapa'),
        ('Khotang','Khotang'), ('Morang','Morang'), ('Okhaldhunga','Okhaldhunga'), ('Panchthar','Panchthar'),
        ('Sankhuwasabha','Sankhuwasabha'), ('Solukhumbu','Solukhumbu'), ('Sunsari','Sunsari'), ('Taplejung','Taplejung'),
        ('Terhathum','Terhathum'), ('Udayapur','Udayapur'),
        ('Saptari','Saptari'), ('Siraha','Siraha'), ('Dhanusha','Dhanusha'), ('Mahottari','Mahottari'),
        ('Sarlahi','Sarlahi'), ('Rautahat','Rautahat'), ('Bara','Bara'), ('Parsa','Parsa'),
        ('Kathmandu','Kathmandu'), ('Bhaktapur','Bhaktapur'), ('Lalitpur','Lalitpur'), ('Kavrepalanchok','Kavrepalanchok'),
        ('Chitwan','Chitwan'), ('Nuwakot','Nuwakot'), ('Dhading','Dhading'), ('Rasuwa','Rasuwa'),
        ('Sindhupalchok','Sindhupalchok'), ('Makwanpur','Makwanpur'), ('Ramechhap','Ramechhap'), ('Dolakha','Dolakha'),
        ('Sindhuli','Sindhuli'), ('Khotang','Khotang'),
        ('Gorkha','Gorkha'), ('Lamjung','Lamjung'), ('Tanahu','Tanahu'), ('Syangja','Syangja'),
        ('Kaski','Kaski'), ('Manang','Manang'), ('Mustang','Mustang'), ('Myagdi','Myagdi'), ('Baglung','Baglung'),
        ('Arghakhanchi','Arghakhanchi'), ('Gulmi','Gulmi'), ('Kapilvastu','Kapilvastu'), ('Nawalpur','Nawalpur'),
        ('Palpa','Palpa'), ('Rupandehi','Rupandehi'), ('Dang','Dang'), ('Bardiya','Bardiya'),
        ('Banke','Banke'), ('Pyuthan','Pyuthan'), ('Rolpa','Rolpa'), ('Rukum East','Rukum East'),
        ('Rukum West','Rukum West'), ('Salyan','Salyan'),
        ('Dailekh','Dailekh'), ('Jajarkot','Jajarkot'), ('Jumla','Jumla'), ('Kalikot','Kalikot'),
        ('Mugu','Mugu'), ('Humla','Humla'), ('Dolpa','Dolpa'), ('Baitadi','Baitadi'),
        ('Darchula','Darchula'), ('Bajhang','Bajhang'), ('Bajura','Bajura'), ('Achham','Achham'),
        ('Doti','Doti'), ('Kailali','Kailali'), ('Kanchanpur','Kanchanpur'), ('Dadeldhura','Dadeldhura'),
    ]


class PatientProfile(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('Unknown', 'Unknown'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    hpass_number = models.CharField(max_length=12, unique=True, editable=False, blank=True)
    health_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True, choices=[
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('prefer_not_to_say', 'Prefer not to say')
    ])
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='Unknown')
    province = models.CharField(max_length=50, choices=NepalLocation.PROVINCE_CHOICES, blank=True)
    district = models.CharField(max_length=50, choices=NepalLocation.DISTRICT_CHOICES, blank=True)
    municipality = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    gender = models.CharField(max_length=20, blank=True, choices=[
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('prefer_not_to_say', 'Prefer not to say')
    ])
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='Unknown')
    address = models.TextField(blank=True)
    allergies = models.TextField(blank=True, help_text="List allergies, one per line")
    chronic_diseases = models.TextField(blank=True, help_text="List chronic diseases, one per line")
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    profile_photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name() or self.user.username}"

    def save(self, *args, **kwargs):
        if not self.hpass_number:
            self.hpass_number = self._generate_unique_hpass()
        super().save(*args, **kwargs)

    def _generate_unique_hpass(self):
        for _ in range(20):
            candidate = f"HP{secrets.randbelow(10**8):08d}"
            if not PatientProfile.objects.filter(hpass_number=candidate).exists():
                return candidate
        raise ValueError("Unable to generate unique HPass number")

    @property
    def health_id_short(self):
        return str(self.health_id).upper()[:8]

    def get_allergies_list(self):
        if self.allergies:
            return [a.strip() for a in self.allergies.split('\n') if a.strip()]
        return []

    def get_chronic_diseases_list(self):
        if self.chronic_diseases:
            return [d.strip() for d in self.chronic_diseases.split('\n') if d.strip()]
        return []


class HospitalProfile(models.Model):
    HOSPITAL_TYPE_CHOICES = [
        ('general', 'General Hospital'),
        ('specialty', 'Specialty Clinic'),
        ('diagnostic', 'Diagnostic Center'),
        ('pharmacy', 'Pharmacy'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile')
    hospital_name = models.CharField(max_length=200)
    hospital_type = models.CharField(max_length=30, choices=HOSPITAL_TYPE_CHOICES, default='general')
    registration_number = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=50, choices=NepalLocation.PROVINCE_CHOICES, blank=True)
    district = models.CharField(max_length=50, choices=NepalLocation.DISTRICT_CHOICES, blank=True)
    municipality = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    logo = models.ImageField(upload_to='hospital_logos/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.hospital_name

    def verify(self):
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()


class Doctor(models.Model):
    nmc_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    name = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='doctor_photos/', blank=True, null=True)
    hospitals = models.ManyToManyField(HospitalProfile, related_name='doctors', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        pieces = [self.name]
        if self.nmc_number:
            pieces.append(f"NMC: {self.nmc_number}")
        if self.specialization:
            pieces.append(self.specialization)
        return ' · '.join(pieces)


class AccessRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revoked', 'Revoked'),
    ]

    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='access_requests')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='access_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Reason for access request")
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('hospital', 'patient')
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.hospital} → {self.patient} ({self.status})"

    def approve(self):
        self.status = 'approved'
        self.responded_at = timezone.now()
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.responded_at = timezone.now()
        self.save()

    def revoke(self):
        self.status = 'revoked'
        self.responded_at = timezone.now()
        self.save()

    @property
    def is_active(self):
        return self.status == 'approved'


class MedicalRecord(models.Model):
    RECORD_TYPE_CHOICES = [
        ('report', 'Medical Report'),
        ('prescription', 'Prescription'),
        ('lab_result', 'Lab Result'),
        ('scan', 'Scan / Imaging'),
        ('vaccination', 'Vaccination'),
        ('discharge', 'Discharge Summary'),
        ('other', 'Other'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_records')
    uploaded_by = models.ForeignKey(HospitalProfile, on_delete=models.SET_NULL, null=True, related_name='uploaded_records')
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True, related_name='records')
    record_type = models.CharField(max_length=30, choices=RECORD_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='medical_records/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    record_date = models.DateField(help_text="Date of the medical event")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")

    class Meta:
        ordering = ['-record_date', '-uploaded_at']

    def __str__(self):
        return f"{self.title} - {self.patient}"

    def verify(self):
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()

    def get_tags_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []

    @property
    def file_extension(self):
        if not self.file:
            return ''
        import os
        _, ext = os.path.splitext(self.file.name)
        return ext.lower()

    @property
    def is_image(self):
        ext = self.file_extension
        return ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']

    @property
    def is_pdf(self):
        return self.file_extension == '.pdf'


class Notification(models.Model):
    NOTIF_TYPE_CHOICES = [
        ('access_request', 'Access Request'),
        ('access_approved', 'Access Approved'),
        ('access_rejected', 'Access Rejected'),
        ('access_revoked', 'Access Revoked'),
        ('record_uploaded', 'Record Uploaded'),
        ('record_verified', 'Record Verified'),
        ('system', 'System'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=NOTIF_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notif for {self.recipient.username}: {self.title}"

    def mark_read(self):
        self.is_read = True
        self.save()
