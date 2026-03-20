from django.contrib import admin
from .models import UserProfile, PatientProfile, HospitalProfile, MedicalRecord, AccessRequest, Notification


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'health_id', 'blood_group', 'gender']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['health_id']


@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):
    list_display = ['hospital_name', 'hospital_type', 'is_verified', 'user']
    list_filter = ['is_verified', 'hospital_type']
    actions = ['verify_hospitals']

    def verify_hospitals(self, request, queryset):
        for hospital in queryset:
            hospital.verify()
        self.message_user(request, f'{queryset.count()} hospital(s) verified.')
    verify_hospitals.short_description = 'Verify selected hospitals'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'uploaded_by', 'record_type', 'is_verified', 'record_date']
    list_filter = ['record_type', 'is_verified']


@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'patient', 'status', 'requested_at']
    list_filter = ['status']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notif_type', 'title', 'is_read', 'created_at']
    list_filter = ['notif_type', 'is_read']
