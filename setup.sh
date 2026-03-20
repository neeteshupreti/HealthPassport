#!/bin/bash
# Health Passport — Quick Setup Script
set -e

echo ""
echo "🏥  Health Passport Setup"
echo "========================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate 2>/dev/null || . venv/bin/activate

echo "📥 Installing dependencies..."
pip install -r requirements.txt -q

echo "🗄️  Running database migrations..."
python manage.py makemigrations core --no-input
python manage.py migrate --no-input

echo ""
echo "👤 Create an admin superuser (for /admin-panel/ and /admin/)"
echo "   Press Ctrl+C to skip this step."
echo ""
python manage.py createsuperuser || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Start the server with:"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "🌐 Then open: http://127.0.0.1:8000"
echo ""
