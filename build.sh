#!/usr/bin/env bash
echo "🚀 Starting build process..."

# 1. Remove everything - database and all migrations
echo "🧹 Cleaning up..."
rm -f db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# 2. Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# 3. Create and apply migrations
echo "📝 Creating migrations..."
python manage.py makemigrations --noinput

echo "🗄️  Applying migrations..."
python manage.py migrate --noinput

# 4. Load initial data
echo "📊 Loading initial data..."
python load_data.py

# 5. Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# 6. Force create superuser
echo "👤 Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()

# Delete existing admin if exists
User.objects.filter(email='admin@admin.com').delete()

# Create fresh superuser (no first_name/last_name - UserManager handles defaults)
User.objects.create_superuser(
    email='admin@admin.com',
    password='admin123'
)
print('✅ Superuser created: admin@admin.com / admin123')

# Create test user
User.objects.create_user(
    email='test@example.com',
    password='test123'
)
print('✅ Test user created: test@example.com / test123')
EOF

echo "✅ Build completed successfully!"