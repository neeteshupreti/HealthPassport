from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, PatientProfile, HospitalProfile, MedicalRecord, AccessRequest, Doctor, NepalLocation


class PatientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-input', 'placeholder': 'Email Address'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Phone Number'}))
    profile_photo = forms.ImageField(required=False, widget=forms.ClearableFileInput(
        attrs={'class': 'form-input-file', 'accept': 'image/*'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Confirm Password'})


class HospitalRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=False, label='Contact Person First Name',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact Person First Name'}))
    last_name = forms.CharField(max_length=100, required=False, label='Contact Person Last Name',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact Person Last Name'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(
        attrs={'class': 'form-input', 'placeholder': 'Hospital Email'}))
    hospital_name = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Full Hospital Name'}))
    hospital_type = forms.ChoiceField(choices=HospitalProfile.HOSPITAL_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}))
    registration_number = forms.CharField(max_length=100, required=False, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Registration / License Number'}))
    province = forms.ChoiceField(choices=[('', 'Select Province')] + list(NepalLocation.PROVINCE_CHOICES), required=False,
        widget=forms.Select(attrs={'class': 'form-input'}))
    district = forms.ChoiceField(choices=[('', 'Select District')] + list(NepalLocation.DISTRICT_CHOICES), required=False,
        widget=forms.Select(attrs={'class': 'form-input'}))
    municipality = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Municipality'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Street / Ward / Locality'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Phone Number'}))
    logo = forms.ImageField(required=False, widget=forms.ClearableFileInput(
        attrs={'class': 'form-input-file', 'accept': 'image/*'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Confirm Password'})


class PatientProfileForm(forms.ModelForm):
    province = forms.ChoiceField(choices=[('', 'Select Province')] + list(NepalLocation.PROVINCE_CHOICES), required=False,
        widget=forms.Select(attrs={'class': 'form-input'}))
    district = forms.ChoiceField(choices=[('', 'Select District')] + list(NepalLocation.DISTRICT_CHOICES), required=False,
        widget=forms.Select(attrs={'class': 'form-input'}))
    municipality = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Municipality'}))

    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'gender', 'blood_group', 'province', 'district', 'municipality', 'address',
                  'allergies', 'chronic_diseases',
                  'emergency_contact_name', 'emergency_contact_phone',
                  'emergency_contact_relation', 'profile_photo']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'blood_group': forms.Select(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'allergies': forms.Textarea(attrs={'class': 'form-input', 'rows': 3,
                'placeholder': 'e.g. Penicillin\nDust\nPeanuts'}),
            'chronic_diseases': forms.Textarea(attrs={'class': 'form-input', 'rows': 3,
                'placeholder': 'e.g. Type 2 Diabetes\nHypertension'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-input'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-input'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': 'form-input',
                'placeholder': 'e.g. Spouse, Parent'}),
        }


class HospitalProfileForm(forms.ModelForm):
    province = forms.ChoiceField(choices=[('', 'Select Province')] + list(NepalLocation.PROVINCE_CHOICES), required=False,
        widget=forms.Select(attrs={'class': 'form-input'}))
    district = forms.ChoiceField(choices=[('', 'Select District')] + list(NepalLocation.DISTRICT_CHOICES), required=False,
        widget=forms.Select(attrs={'class': 'form-input'}))
    municipality = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Municipality'}))

    class Meta:
        model = HospitalProfile
        fields = ['hospital_name', 'hospital_type', 'registration_number', 'province', 'district', 'municipality',
                  'address', 'website', 'description', 'logo']
        widgets = {
            'hospital_name': forms.TextInput(attrs={'class': 'form-input'}),
            'hospital_type': forms.Select(attrs={'class': 'form-input'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }


class MedicalRecordForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.none(), required=False,
        widget=forms.Select(attrs={'class': 'form-input'}),
        label='Attending Doctor (optional)')

    class Meta:
        model = MedicalRecord
        fields = ['record_type', 'title', 'description', 'doctor', 'record_date', 'tags']
        widgets = {
            'record_type': forms.Select(attrs={'class': 'form-input'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Record Title'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 5,
                'placeholder': 'Describe the record, key findings, diagnosis, or treatment notes...'}),
            'record_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'tags': forms.TextInput(attrs={'class': 'form-input',
                'placeholder': 'e.g. cardiology, annual, blood test'}),
        }

    def __init__(self, *args, hospital=None, **kwargs):
        super().__init__(*args, **kwargs)
        if hospital is not None:
            self.fields['doctor'].queryset = Doctor.objects.filter(hospitals=hospital).order_by('name')
        else:
            self.fields['doctor'].queryset = Doctor.objects.all().order_by('name')



class AccessRequestForm(forms.ModelForm):
    class Meta:
        model = AccessRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-input', 'rows': 4,
                'placeholder': 'Explain why you need access to this patient\'s records...'}),
        }


class PatientSearchForm(forms.Form):
    health_id = forms.CharField(max_length=100, required=False, label='Health ID',
        widget=forms.TextInput(attrs={'class': 'form-input',
            'placeholder': 'Enter patient Health ID (e.g. A1B2C3D4)'}))
    name = forms.CharField(max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input',
            'placeholder': 'Or search by patient name'}))


class HPassLookupForm(forms.Form):
    hpass_number = forms.CharField(max_length=12, required=True, label='HPass Number',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'HPass Number (e.g. HP00001234)'}))
    date_of_birth = forms.DateField(required=True, label='Date of Birth',
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}))


class ReportIssueForm(forms.Form):
    hospital = forms.ChoiceField(
        label='Report to',
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describe the issue you encountered...'}),
        required=True
    )

    def __init__(self, *args, hospitals=None, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', 'Support / Admin')]
        if hospitals is not None:
            choices += [(str(h.id), h.hospital_name) for h in hospitals]
        self.fields['hospital'].choices = choices


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['nmc_number', 'name', 'specialization', 'email', 'phone', 'photo', 'hospitals']
        widgets = {
            'nmc_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'NMC Number'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Doctor full name'}),
            'specialization': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Specialization (e.g. Cardiology)'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-input-file', 'accept': 'image/*'}),
            'hospitals': forms.SelectMultiple(attrs={'class': 'form-input'}),
        }


class AssignDoctorForm(forms.Form):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.none(),
                                    widget=forms.Select(attrs={'class': 'form-input'}),
                                    label='Select doctor to assign',
                                    empty_label='Choose doctor')

    def __init__(self, *args, hospital=None, doctors=None, **kwargs):
        super().__init__(*args, **kwargs)
        if doctors is not None:
            qs = doctors.order_by('name')
        else:
            qs = Doctor.objects.all().order_by('name')

        if hospital is not None:
            qs = qs.exclude(hospitals=hospital)

        self.fields['doctor'].queryset = qs


class AdminDoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['nmc_number', 'name', 'specialization', 'email', 'phone', 'photo', 'hospitals']
        widgets = {
            'nmc_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'NMC Number'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Doctor full name'}),
            'specialization': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Specialization (e.g. Cardiology)'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-input-file', 'accept': 'image/*'}),
            'hospitals': forms.SelectMultiple(attrs={'class': 'form-input'}),
        }


class AdminUserForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        required=True,
        label='Role (patient / hospital / admin)'
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email address'}),
        }

    def __init__(self, *args, profile: UserProfile | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if profile is not None:
            self.fields['role'].initial = profile.role
            self.fields['phone'].initial = profile.phone

    def save(self, commit=True):
        user = super().save(commit=commit)
        # Ensure profile exists and is updated
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = self.cleaned_data.get('role')
        profile.phone = self.cleaned_data.get('phone', '')
        if commit:
            profile.save()
        return user
