from django.db import migrations
import secrets


def generate_hpass(apps, schema_editor):
    PatientProfile = apps.get_model('core', 'PatientProfile')
    for patient in PatientProfile.objects.filter(hpass_number=''):
        for _ in range(20):
            candidate = f"HP{secrets.randbelow(10**8):08d}"
            if not PatientProfile.objects.filter(hpass_number=candidate).exists():
                patient.hpass_number = candidate
                patient.save(update_fields=['hpass_number'])
                break


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_patientprofile_hpass_number_doctor_and_more'),
    ]

    operations = [
        migrations.RunPython(generate_hpass, reverse_code=migrations.RunPython.noop),
    ]
