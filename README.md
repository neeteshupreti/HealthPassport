# 🏥 Health Passport — Unified Digital Medical Record System

A secure Django web application for managing digital medical records, built for a hackathon. Patients store and control their health data; hospitals upload and verify records.

---

## 🚀 Quick Start

```bash
# 1. Clone / extract the project
cd health_passport

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py makemigrations core
python manage.py migrate

# 5. Create an admin superuser
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## 👥 User Roles

| Role     | What they can do |
|----------|-----------------|
| **Patient**  | Register with unique Health ID, view/download records, manage hospital access, share QR emergency profile |
| **Hospital** | Request access to patients, upload & verify medical records, manage linked patients |
| **Admin**    | Verify hospitals, view system stats via `/admin-panel/` and Django admin `/admin/` |

---

## 📋 Features

### 🆔 Digital Health ID
- Every patient gets a UUID-based Health ID
- Short 8-character display code (e.g. `A1B2C3D4`)
- QR code generated automatically on registration
- QR links to a **public emergency profile page**

### 📄 Medical Records
- Hospitals upload: Reports, Prescriptions, Lab Results, Scans, Vaccinations, Discharge Summaries
- All hospital-uploaded records are auto-marked **Verified**
- Patients can view and download any of their records
- File types: PDF, JPG, PNG (max 10MB)

### 🔐 Access Control
- Hospitals must **request access** from patients
- Patients can **approve**, **reject**, or **revoke** at any time
- Hospitals can only see records of patients who approved them
- Full audit trail with timestamps

### 🚨 Emergency QR Profile (Public)
- No login required to view
- Shows: Blood group, allergies, chronic conditions, emergency contact
- Tap-to-call emergency contact button
- Accessible at `/emergency/<health-id>/`

### 📊 Health Timeline
- Chronological view of all records
- Grouped by year
- Filter by record type
- Shows hospital name and date for each entry

### 🔔 Notification System
- In-app notifications for all key events
- Real-time badge count in navbar
- Events: access requests, approvals, rejections, revocations, record uploads

---

## 🗂️ Project Structure

```
health_passport/
├── manage.py
├── requirements.txt
├── health_passport/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                         # Main application
│   ├── models.py                 # Database models
│   ├── views.py                  # All view logic
│   ├── forms.py                  # Form definitions & validation
│   ├── urls.py                   # URL routing
│   ├── decorators.py             # Role-based access decorators
│   ├── utils.py                  # QR code generation utility
│   ├── context_processors.py     # Notification badge count
│   └── admin.py                  # Django admin config
├── templates/
│   ├── core/                     # Shared templates (base, home, login, register, emergency)
│   ├── patient/                  # Patient-facing templates
│   ├── hospital/                 # Hospital-facing templates
│   └── admin_panel/              # Custom admin panel
├── static/                       # CSS, JS, images (add your own)
└── media/                        # User uploads (auto-created)
```

---

## 🗄️ Database Models

| Model | Key Fields |
|-------|-----------|
| `UserProfile` | user, role (patient/hospital/admin), phone |
| `PatientProfile` | health_id (UUID), blood_group, allergies, chronic_diseases, emergency_contact, qr_code |
| `HospitalProfile` | hospital_name, hospital_type, registration_number, is_verified |
| `MedicalRecord` | patient, uploaded_by, record_type, file, is_verified, record_date |
| `AccessRequest` | hospital, patient, status (pending/approved/rejected/revoked), message |
| `Notification` | recipient, notif_type, title, message, is_read |

---

## 🔗 Key URLs

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/register/` | Choose account type |
| `/register/patient/` | Patient registration |
| `/register/hospital/` | Hospital registration |
| `/login/` | Login |
| `/patient/` | Patient dashboard |
| `/patient/records/` | View all records |
| `/patient/timeline/` | Health timeline |
| `/patient/access-requests/` | Manage hospital access |
| `/hospital/` | Hospital dashboard |
| `/hospital/search/` | Search patients |
| `/hospital/patients/` | Linked patients |
| `/hospital/patients/<id>/upload/` | Upload record |
| `/emergency/<uuid>/` | Public QR emergency profile |
| `/notifications/` | All notifications |
| `/admin-panel/` | Custom admin dashboard |
| `/admin/` | Django admin |

---

## 🔧 Configuration

Edit `health_passport/settings.py`:

```python
# For production, change this:
SECRET_KEY = 'your-production-secret-key'
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

# Database (default: SQLite; swap for PostgreSQL in production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'healthpassport',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
    }
}
```

---

## 🔒 Security Notes

- Role decorators (`@patient_required`, `@hospital_required`) protect all sensitive views
- Hospital access to patient records is checked on every request
- File upload restricted to PDF/JPG/PNG, max 10MB
- CSRF protection on all forms
- Emergency profile is intentionally public (read-only, minimal info)
- For production: set `DEBUG=False`, use environment variables for secrets, configure proper media storage (e.g. AWS S3)

---

## 📦 Dependencies

```
Django==4.2.7       # Web framework
qrcode==7.4.2       # QR code image generation
Pillow==10.1.0      # Image processing (required by qrcode and ImageField)
```

---

Health Passport demonstrates:
- Clean 3-tier Django architecture
- Role-based access control without third-party packages
- Patient-controlled data sharing
- Real-world healthcare workflow simulation
- Mobile-friendly responsive UI

---

*Made with ❤️ for better healthcare access*
