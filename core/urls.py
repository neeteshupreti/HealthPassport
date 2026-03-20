from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('register/', views.register_choice, name='register_choice'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/hospital/', views.register_hospital, name='register_hospital'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('emergency/<uuid:health_id>/', views.emergency_profile, name='emergency_profile'),
    path('scan/<str:identifier>/', views.scan_profile, name='scan_profile'),
    path('lookup/', views.lookup_records, name='lookup_records'),
    path('scan-qr/', views.qr_scanner, name='qr_scanner'),

    # Patient
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/profile/edit/', views.patient_profile_edit, name='patient_profile_edit'),
    path('patient/records/', views.patient_records, name='patient_records'),
    path('patient/timeline/', views.patient_timeline, name='patient_timeline'),
    path('patient/report-issue/', views.patient_report_issue, name='patient_report_issue'),
    path('patient/access-requests/', views.patient_access_requests, name='patient_access_requests'),
    path('patient/access-requests/<int:request_id>/<str:action>/', views.respond_access_request, name='respond_access_request'),
    path('hospital/link-patient/<int:patient_id>/', views.hospital_link_patient, name='hospital_link_patient'),
    path('hospital/unlink-patient/<int:patient_id>/', views.hospital_unlink_patient, name='hospital_unlink_patient'),
    path('patient/records/<int:record_id>/download/', views.download_record, name='download_record'),
    path('patient/qr/regenerate/', views.regenerate_qr, name='regenerate_qr'),

    # Hospital
    path('hospital/', views.hospital_dashboard, name='hospital_dashboard'),
    path('hospital/profile/edit/', views.hospital_profile_edit, name='hospital_profile_edit'),
    path('hospital/search/', views.hospital_search_patient, name='hospital_search_patient'),
    path('hospital/request-access/<int:patient_id>/', views.hospital_request_access, name='hospital_request_access'),
    path('hospital/patients/', views.hospital_patients, name='hospital_patients'),
    path('hospital/patients/<int:patient_id>/records/', views.hospital_patient_records, name='hospital_patient_records'),
    path('hospital/patients/<int:patient_id>/upload/', views.hospital_upload_record, name='hospital_upload_record'),
    path('hospital/doctors/', views.hospital_doctors, name='hospital_doctors'),
    path('hospital/doctors/add/', views.hospital_add_doctor, name='hospital_add_doctor'),
    path('hospital/doctors/<int:doctor_id>/edit/', views.hospital_edit_doctor, name='hospital_edit_doctor'),
    path('hospital/doctors/<int:doctor_id>/delete/', views.hospital_delete_doctor, name='hospital_delete_doctor'),

    path('doctors/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),

    path('admin-panel/doctors/', views.admin_doctors, name='admin_doctors'),
    path('admin-panel/doctors/add/', views.admin_add_doctor, name='admin_add_doctor'),
    path('admin-panel/doctors/<int:doctor_id>/edit/', views.admin_edit_doctor, name='admin_edit_doctor'),
    path('admin-panel/doctors/<int:doctor_id>/delete/', views.admin_delete_doctor, name='admin_delete_doctor'),

    path('admin-panel/patients/', views.admin_patients, name='admin_patients'),
    path('admin-panel/patients/add/', views.register_patient, name='admin_add_patient'),
    path('admin-panel/patients/<int:patient_id>/edit/', views.admin_edit_patient, name='admin_edit_patient'),
    path('admin-panel/patients/<int:patient_id>/delete/', views.admin_delete_patient, name='admin_delete_patient'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),

    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/<int:user_id>/edit/', views.admin_edit_user, name='admin_edit_user'),
    path('admin-panel/hospitals/', views.admin_hospitals, name='admin_hospitals'),
    path('admin-panel/hospitals/<int:hospital_id>/edit/', views.admin_edit_hospital, name='admin_edit_hospital'),
    path('admin-panel/verify/<int:hospital_id>/', views.admin_verify_hospital, name='admin_verify_hospital'),
]
