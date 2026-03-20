import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings


def generate_patient_qr(patient_profile, request=None):
    """Generate QR code for patient emergency profile.

    The QR encodes a URL that includes the patient's **HPass number**.
    """

    identifier = patient_profile.hpass_number or str(patient_profile.health_id)

    if request:
        base_url = request.build_absolute_uri('/')
        url = f"{base_url.rstrip('/')}/scan/{identifier}/"
    else:
        url = f"http://localhost:8000/scan/{identifier}/"

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1a56db", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    safe_id = identifier.replace('/', '_')
    filename = f"qr_{safe_id}.png"
    patient_profile.qr_code.save(filename, ContentFile(buffer.read()), save=True)

    return patient_profile.qr_code
