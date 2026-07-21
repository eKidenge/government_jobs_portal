# load_data.py
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'government_jobs_portal.settings')

import django
django.setup()

from decimal import Decimal
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

User = get_user_model()


def load_payment_plans():
    """Load payment plans into the database"""
    from payments.models import PaymentPlan
    
    print("📊 Loading payment plans...")
    
    plans_data = [
        {
            'plan_type': 'single',
            'name': 'Single Application',
            'amount': Decimal('300.00'),
            'currency': 'KES',
            'duration_days': 30,
            'description': 'Apply to 1 job with full access to job details and application tracking.',
            'features': [
                'Apply to 1 job',
                'Valid for 30 days',
                'Access to job details',
                'Application tracking',
                'Email notifications'
            ],
            'is_active': True,
            'popular': False,
            'recommended': False,
            'sort_order': 1
        },
        {
            'plan_type': 'monthly',
            'name': 'Monthly Access',
            'amount': Decimal('1000.00'),
            'currency': 'KES',
            'duration_days': 30,
            'description': 'Full monthly access to all jobs with unlimited applications.',
            'features': [
                'Unlimited applications',
                'Valid for 30 days',
                'Full job access',
                'Priority support',
                'Application tracking',
                'Email notifications',
                'Job alerts'
            ],
            'is_active': True,
            'popular': True,
            'recommended': False,
            'sort_order': 2
        },
        {
            'plan_type': 'quarterly',
            'name': 'Quarterly Access',
            'amount': Decimal('2500.00'),
            'currency': 'KES',
            'duration_days': 90,
            'description': 'Three months of full access with unlimited applications.',
            'features': [
                'Unlimited applications',
                'Valid for 90 days',
                'Full job access',
                'Priority support',
                'Application tracking',
                'Email notifications',
                'Job alerts',
                'Save up to 17%'
            ],
            'is_active': True,
            'popular': False,
            'recommended': True,
            'sort_order': 3
        },
        {
            'plan_type': 'annual',
            'name': 'Annual Access',
            'amount': Decimal('8000.00'),
            'currency': 'KES',
            'duration_days': 365,
            'description': 'Full year of unlimited access with premium features.',
            'features': [
                'Unlimited applications',
                'Valid for 365 days',
                'Full job access',
                'Priority support',
                'Application tracking',
                'Email notifications',
                'Job alerts',
                'Save up to 33%',
                'Early access to jobs'
            ],
            'is_active': True,
            'popular': False,
            'recommended': False,
            'sort_order': 4
        },
        {
            'plan_type': 'premium',
            'name': 'Premium Access',
            'amount': Decimal('15000.00'),
            'currency': 'KES',
            'duration_days': 365,
            'description': 'Premium full-year access with exclusive benefits.',
            'features': [
                'Unlimited applications',
                'Valid for 365 days',
                'Full job access',
                'VIP support',
                'Application tracking',
                'Email notifications',
                'Job alerts',
                'Early access to jobs',
                'CV review service',
                'Interview coaching'
            ],
            'is_active': True,
            'popular': False,
            'recommended': False,
            'sort_order': 5
        }
    ]
    
    created_count = 0
    for plan_data in plans_data:
        plan, created = PaymentPlan.objects.get_or_create(
            plan_type=plan_data['plan_type'],
            defaults=plan_data
        )
        if created:
            created_count += 1
            print(f"  ✅ Created plan: {plan.name}")
        else:
            updated = False
            for key, value in plan_data.items():
                if getattr(plan, key) != value:
                    setattr(plan, key, value)
                    updated = True
            if updated:
                plan.save()
                print(f"  🔄 Updated plan: {plan.name}")
            else:
                print(f"  ℹ️ Plan already exists: {plan.name}")
    
    print(f"✅ Loaded {created_count} new payment plans")
    return created_count


def load_countries():
    """Load countries into the database"""
    from jobs.models import Country
    
    print("📊 Loading countries...")
    
    countries_data = [
        {'name': 'Kenya', 'code': 'KE', 'currency': 'KES', 'currency_symbol': 'KSh', 'description': 'East African nation', 'is_active': True},
        {'name': 'United Kingdom', 'code': 'GB', 'currency': 'GBP', 'currency_symbol': '£', 'description': 'United Kingdom of Great Britain and Northern Ireland', 'is_active': True},
        {'name': 'United States', 'code': 'US', 'currency': 'USD', 'currency_symbol': '$', 'description': 'United States of America', 'is_active': True},
        {'name': 'Canada', 'code': 'CA', 'currency': 'CAD', 'currency_symbol': 'C$', 'description': 'North American country', 'is_active': True},
        {'name': 'Australia', 'code': 'AU', 'currency': 'AUD', 'currency_symbol': 'A$', 'description': 'Australian continent', 'is_active': True},
        {'name': 'Germany', 'code': 'DE', 'currency': 'EUR', 'currency_symbol': '€', 'description': 'Central European country', 'is_active': True},
        {'name': 'United Arab Emirates', 'code': 'AE', 'currency': 'AED', 'currency_symbol': 'د.إ', 'description': 'Middle Eastern country', 'is_active': True},
        {'name': 'South Africa', 'code': 'ZA', 'currency': 'ZAR', 'currency_symbol': 'R', 'description': 'Southern African nation', 'is_active': True},
        {'name': 'Nigeria', 'code': 'NG', 'currency': 'NGN', 'currency_symbol': '₦', 'description': 'West African nation', 'is_active': True},
        {'name': 'Ghana', 'code': 'GH', 'currency': 'GHS', 'currency_symbol': 'GH₵', 'description': 'West African nation', 'is_active': True},
        {'name': 'Tanzania', 'code': 'TZ', 'currency': 'TZS', 'currency_symbol': 'TSh', 'description': 'East African nation', 'is_active': True},
        {'name': 'Uganda', 'code': 'UG', 'currency': 'UGX', 'currency_symbol': 'USh', 'description': 'East African nation', 'is_active': True},
        {'name': 'Rwanda', 'code': 'RW', 'currency': 'RWF', 'currency_symbol': 'FRw', 'description': 'East African nation', 'is_active': True},
        {'name': 'India', 'code': 'IN', 'currency': 'INR', 'currency_symbol': '₹', 'description': 'South Asian country', 'is_active': True},
        {'name': 'China', 'code': 'CN', 'currency': 'CNY', 'currency_symbol': '¥', 'description': 'East Asian country', 'is_active': True},
        {'name': 'Brazil', 'code': 'BR', 'currency': 'BRL', 'currency_symbol': 'R$', 'description': 'South American country', 'is_active': True},
        {'name': 'France', 'code': 'FR', 'currency': 'EUR', 'currency_symbol': '€', 'description': 'Western European country', 'is_active': True},
        {'name': 'Italy', 'code': 'IT', 'currency': 'EUR', 'currency_symbol': '€', 'description': 'Southern European country', 'is_active': True},
        {'name': 'Spain', 'code': 'ES', 'currency': 'EUR', 'currency_symbol': '€', 'description': 'Southwestern European country', 'is_active': True},
        {'name': 'Japan', 'code': 'JP', 'currency': 'JPY', 'currency_symbol': '¥', 'description': 'East Asian country', 'is_active': True},
        {'name': 'Netherlands', 'code': 'NL', 'currency': 'EUR', 'currency_symbol': '€', 'description': 'Northwestern European country', 'is_active': True},
        {'name': 'Sweden', 'code': 'SE', 'currency': 'SEK', 'currency_symbol': 'kr', 'description': 'Nordic country', 'is_active': True},
        {'name': 'Norway', 'code': 'NO', 'currency': 'NOK', 'currency_symbol': 'kr', 'description': 'Nordic country', 'is_active': True},
        {'name': 'Denmark', 'code': 'DK', 'currency': 'DKK', 'currency_symbol': 'kr', 'description': 'Nordic country', 'is_active': True},
        {'name': 'Finland', 'code': 'FI', 'currency': 'EUR', 'currency_symbol': '€', 'description': 'Nordic country', 'is_active': True},
        {'name': 'Ireland', 'code': 'IE', 'currency': 'EUR', 'currency_symbol': '€', 'description': 'Western European country', 'is_active': True},
        {'name': 'New Zealand', 'code': 'NZ', 'currency': 'NZD', 'currency_symbol': 'NZ$', 'description': 'Island country in the South Pacific', 'is_active': True},
        {'name': 'Singapore', 'code': 'SG', 'currency': 'SGD', 'currency_symbol': 'S$', 'description': 'Southeast Asian city-state', 'is_active': True},
        {'name': 'Malaysia', 'code': 'MY', 'currency': 'MYR', 'currency_symbol': 'RM', 'description': 'Southeast Asian country', 'is_active': True},
        {'name': 'Qatar', 'code': 'QA', 'currency': 'QAR', 'currency_symbol': 'ر.ق', 'description': 'Middle Eastern country', 'is_active': True},
        {'name': 'Saudi Arabia', 'code': 'SA', 'currency': 'SAR', 'currency_symbol': 'ر.س', 'description': 'Middle Eastern country', 'is_active': True},
        {'name': 'Kuwait', 'code': 'KW', 'currency': 'KWD', 'currency_symbol': 'د.ك', 'description': 'Middle Eastern country', 'is_active': True},
        {'name': 'Oman', 'code': 'OM', 'currency': 'OMR', 'currency_symbol': 'ر.ع.', 'description': 'Middle Eastern country', 'is_active': True},
        {'name': 'Bahrain', 'code': 'BH', 'currency': 'BHD', 'currency_symbol': 'د.ب', 'description': 'Middle Eastern country', 'is_active': True},
        {'name': 'Mexico', 'code': 'MX', 'currency': 'MXN', 'currency_symbol': '$', 'description': 'North American country', 'is_active': True},
        {'name': 'Argentina', 'code': 'AR', 'currency': 'ARS', 'currency_symbol': '$', 'description': 'South American country', 'is_active': True},
        {'name': 'Chile', 'code': 'CL', 'currency': 'CLP', 'currency_symbol': '$', 'description': 'South American country', 'is_active': True},
        {'name': 'Colombia', 'code': 'CO', 'currency': 'COP', 'currency_symbol': '$', 'description': 'South American country', 'is_active': True},
        {'name': 'Peru', 'code': 'PE', 'currency': 'PEN', 'currency_symbol': 'S/', 'description': 'South American country', 'is_active': True},
        {'name': 'Turkey', 'code': 'TR', 'currency': 'TRY', 'currency_symbol': '₺', 'description': 'Eurasian country', 'is_active': True},
        {'name': 'Greece', 'code': 'GR', 'currency': 'EUR', 'currency_symbol': '€', 'description': 'Southern European country', 'is_active': True},
        {'name': 'Portugal', 'code': 'PT', 'currency': 'EUR', 'currency_symbol': '€', 'description': 'Southwestern European country', 'is_active': True},
        {'name': 'Belgium', 'code': 'BE', 'currency': 'EUR', 'currency_symbol': '€', 'description': 'Western European country', 'is_active': True},
        {'name': 'Switzerland', 'code': 'CH', 'currency': 'CHF', 'currency_symbol': 'Fr', 'description': 'Central European country', 'is_active': True},
        {'name': 'Austria', 'code': 'AT', 'currency': 'EUR', 'currency_symbol': '€', 'description': 'Central European country', 'is_active': True},
    ]
    
    created_count = 0
    for country_data in countries_data:
        country, created = Country.objects.get_or_create(
            code=country_data['code'],
            defaults=country_data
        )
        if created:
            created_count += 1
            print(f"  ✅ Created country: {country.name}")
        else:
            print(f"  ℹ️ Country already exists: {country.name}")
    
    print(f"✅ Loaded {created_count} new countries")
    return created_count


def load_categories():
    """Load categories into the database"""
    from jobs.models import Category
    
    print("📊 Loading categories...")
    
    categories_data = [
        {'name': 'Government & Public Sector', 'icon': 'fa-landmark', 'description': 'Government and public sector positions', 'is_active': True},
        {'name': 'Administration', 'icon': 'fa-briefcase', 'description': 'Administrative and office management roles', 'is_active': True},
        {'name': 'Finance & Accounting', 'icon': 'fa-calculator', 'description': 'Financial management and accounting positions', 'is_active': True},
        {'name': 'Human Resources', 'icon': 'fa-users', 'description': 'HR and personnel management roles', 'is_active': True},
        {'name': 'Information Technology', 'icon': 'fa-laptop-code', 'description': 'IT and technology positions', 'is_active': True},
        {'name': 'Legal', 'icon': 'fa-gavel', 'description': 'Legal and compliance roles', 'is_active': True},
        {'name': 'Health & Medical', 'icon': 'fa-heartbeat', 'description': 'Healthcare and medical positions', 'is_active': True},
        {'name': 'Education & Training', 'icon': 'fa-graduation-cap', 'description': 'Teaching and education roles', 'is_active': True},
        {'name': 'Engineering', 'icon': 'fa-microchip', 'description': 'Engineering and technical roles', 'is_active': True},
        {'name': 'Agriculture & Farming', 'icon': 'fa-seedling', 'description': 'Agricultural and environmental positions', 'is_active': True},
        {'name': 'Security & Defense', 'icon': 'fa-shield-alt', 'description': 'Security and defense roles', 'is_active': True},
        {'name': 'Transport & Logistics', 'icon': 'fa-truck', 'description': 'Transportation and logistics positions', 'is_active': True},
        {'name': 'Communications & Media', 'icon': 'fa-bullhorn', 'description': 'Communications and media roles', 'is_active': True},
        {'name': 'Research & Development', 'icon': 'fa-flask', 'description': 'Research and development positions', 'is_active': True},
        {'name': 'Customer Service', 'icon': 'fa-headset', 'description': 'Customer service and support roles', 'is_active': True},
        {'name': 'Hospitality & Tourism', 'icon': 'fa-hotel', 'description': 'Hospitality and tourism positions', 'is_active': True},
        {'name': 'Construction & Building', 'icon': 'fa-hard-hat', 'description': 'Construction and building roles', 'is_active': True},
        {'name': 'Manufacturing & Production', 'icon': 'fa-industry', 'description': 'Manufacturing and production positions', 'is_active': True},
        {'name': 'Sales & Marketing', 'icon': 'fa-chart-line', 'description': 'Sales and marketing roles', 'is_active': True},
        {'name': 'Real Estate & Property', 'icon': 'fa-home', 'description': 'Real estate and property positions', 'is_active': True},
        {'name': 'Art & Design', 'icon': 'fa-palette', 'description': 'Creative and artistic roles', 'is_active': True},
        {'name': 'Science & Laboratory', 'icon': 'fa-flask', 'description': 'Scientific and laboratory positions', 'is_active': True},
        {'name': 'Social Services', 'icon': 'fa-hand-holding-heart', 'description': 'Social work and community services', 'is_active': True},
        {'name': 'Sports & Fitness', 'icon': 'fa-running', 'description': 'Sports and fitness roles', 'is_active': True},
        {'name': 'Aviation & Aerospace', 'icon': 'fa-plane', 'description': 'Aviation and aerospace positions', 'is_active': True},
        {'name': 'Maritime & Shipping', 'icon': 'fa-ship', 'description': 'Maritime and shipping roles', 'is_active': True},
        {'name': 'Mining & Resources', 'icon': 'fa-gem', 'description': 'Mining and natural resources positions', 'is_active': True},
        {'name': 'Energy & Utilities', 'icon': 'fa-bolt', 'description': 'Energy and utility services roles', 'is_active': True},
        {'name': 'Telecommunications', 'icon': 'fa-phone', 'description': 'Telecommunications positions', 'is_active': True},
        {'name': 'Insurance', 'icon': 'fa-shield-alt', 'description': 'Insurance and risk management roles', 'is_active': True},
    ]
    
    created_count = 0
    for category_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=category_data['name'],
            defaults=category_data
        )
        if created:
            created_count += 1
            print(f"  ✅ Created category: {category.name}")
        else:
            print(f"  ℹ️ Category already exists: {category.name}")
    
    print(f"✅ Loaded {created_count} new categories")
    return created_count


def load_employers():
    """Load employers into the database"""
    from employers.models import EmployerProfile
    from accounts.models import User
    from jobs.models import Country
    
    print("📊 Loading employers...")
    
    try:
        kenya = Country.objects.get(code='KE')
        uk = Country.objects.get(code='GB')
        usa = Country.objects.get(code='US')
        canada = Country.objects.get(code='CA')
        australia = Country.objects.get(code='AU')
        south_africa = Country.objects.get(code='ZA')
        nigeria = Country.objects.get(code='NG')
        tanzania = Country.objects.get(code='TZ')
        uganda = Country.objects.get(code='UG')
        rwanda = Country.objects.get(code='RW')
        uae = Country.objects.get(code='AE')
        germany = Country.objects.get(code='DE')
    except Country.DoesNotExist:
        print("  ⚠️ Countries not found, run load_countries first")
        return 0
    
    employers_data = [
        {
            'company_name': 'Kenya Commercial Bank',
            'registration_number': 'KCB/2024/001',
            'license_number': 'KCB-LIC-001',
            'industry': 'finance',
            'contact_phone': '+254-20-222-5678',
            'contact_email': 'info@kcb.co.ke',
            'address': 'KCB Towers, Kenyatta Avenue, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'description': 'Leading commercial bank in East Africa with over 200 branches',
            'website': 'https://www.kcb.co.ke',
            'company_size': '500+'
        },
        {
            'company_name': 'Safaricom PLC',
            'registration_number': 'SAF/2024/002',
            'license_number': 'SAF-LIC-002',
            'industry': 'ict',
            'contact_phone': '+254-20-222-5679',
            'contact_email': 'info@safaricom.co.ke',
            'address': 'Safaricom House, Waiyaki Way, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'description': 'Leading telecommunications company in Kenya with 40M+ subscribers',
            'website': 'https://www.safaricom.co.ke',
            'company_size': '500+'
        },
        {
            'company_name': 'Equity Bank Kenya',
            'registration_number': 'EQT/2024/003',
            'license_number': 'EQT-LIC-003',
            'industry': 'finance',
            'contact_phone': '+254-20-222-5680',
            'contact_email': 'info@equitybank.co.ke',
            'address': 'Equity Centre, Hospital Road, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'description': 'Leading financial services provider with presence in 6 countries',
            'website': 'https://www.equitybank.co.ke',
            'company_size': '500+'
        },
        {
            'company_name': 'Kenya Airways',
            'registration_number': 'KQ/2024/004',
            'license_number': 'KQ-LIC-004',
            'industry': 'transport',
            'contact_phone': '+254-20-222-5681',
            'contact_email': 'info@kenya-airways.com',
            'address': 'Embakasi, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'description': 'Flag carrier airline of Kenya with flights to 50+ destinations',
            'website': 'https://www.kenya-airways.com',
            'company_size': '500+'
        },
        {
            'company_name': 'Nation Media Group',
            'registration_number': 'NMG/2024/005',
            'license_number': 'NMG-LIC-005',
            'industry': 'other',
            'contact_phone': '+254-20-222-5682',
            'contact_email': 'info@nationmedia.com',
            'address': 'Nation Centre, Kimathi Street, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'description': 'Leading media house in East Africa with multiple publications',
            'website': 'https://www.nationmedia.com',
            'company_size': '500+'
        },
        {
            'company_name': 'Brookside Dairy Limited',
            'registration_number': 'BRK/2024/006',
            'license_number': 'BRK-LIC-006',
            'industry': 'manufacturing',
            'contact_phone': '+254-20-222-5683',
            'contact_email': 'info@brookside.co.ke',
            'address': 'Brookside Drive, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'description': 'Leading dairy processor in East Africa',
            'website': 'https://www.brookside.co.ke',
            'company_size': '500+'
        },
        {
            'company_name': 'KCB Insurance Agency',
            'registration_number': 'KCB/2024/007',
            'license_number': 'KCB-LIC-007',
            'industry': 'finance',
            'contact_phone': '+254-20-222-5684',
            'contact_email': 'info@kcbinsurance.co.ke',
            'address': 'KCB Towers, Nairobi, Kenya',
            'country': kenya,
            'is_verified': False,
            'description': 'Leading insurance provider in East Africa',
            'website': 'https://www.kcbinsurance.co.ke',
            'company_size': '201-500'
        },
        {
            'company_name': 'Jubilee Holdings Limited',
            'registration_number': 'JHL/2024/008',
            'license_number': 'JHL-LIC-008',
            'industry': 'finance',
            'contact_phone': '+254-20-222-5685',
            'contact_email': 'info@jubilee.co.ke',
            'address': 'Jubilee House, Mama Ngina Street, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'description': 'Leading insurance and investment group in East Africa',
            'website': 'https://www.jubilee.co.ke',
            'company_size': '500+'
        },
        {
            'company_name': 'Royal Media Services',
            'registration_number': 'RMS/2024/009',
            'license_number': 'RMS-LIC-009',
            'industry': 'other',
            'contact_phone': '+254-20-222-5686',
            'contact_email': 'info@royalmedia.co.ke',
            'address': 'Royal Media Services, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'description': 'Leading media company in Kenya',
            'website': 'https://www.royalmedia.co.ke',
            'company_size': '201-500'
        },
        {
            'company_name': 'Kakuzi PLC',
            'registration_number': 'KKZ/2024/010',
            'license_number': 'KKZ-LIC-010',
            'industry': 'agriculture',
            'contact_phone': '+254-20-222-5687',
            'contact_email': 'info@kakuzi.co.ke',
            'address': 'Kakuzi, Thika, Kenya',
            'country': kenya,
            'is_verified': True,
            'description': 'Leading agribusiness company in Kenya',
            'website': 'https://www.kakuzi.co.ke',
            'company_size': '201-500'
        },
        {
            'company_name': 'British American Tobacco Kenya',
            'registration_number': 'BAT/2024/011',
            'license_number': 'BAT-LIC-011',
            'industry': 'manufacturing',
            'contact_phone': '+254-20-222-5688',
            'contact_email': 'info@batkenya.co.ke',
            'address': 'BAT House, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'description': 'Leading tobacco company in Kenya',
            'website': 'https://www.batkenya.co.ke',
            'company_size': '201-500'
        },
        {
            'company_name': 'Shell Kenya Limited',
            'registration_number': 'SHE/2024/012',
            'license_number': 'SHE-LIC-012',
            'industry': 'energy',
            'contact_phone': '+254-20-222-5689',
            'contact_email': 'info@shell.co.ke',
            'address': 'Shell House, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'description': 'Leading energy and petroleum company in Kenya',
            'website': 'https://www.shell.co.ke',
            'company_size': '201-500'
        }
    ]
    
    created_count = 0
    for employer_data in employers_data:
        try:
            email = f"{employer_data['company_name'].lower().replace(' ', '').replace('&', '').replace('.', '')}@employer.com"
            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': f"{employer_data['company_name']} Admin",
                    'phone_number': f"0712345{600+created_count:02d}",
                    'user_type': 'employer',
                    'status': 'approved',
                    'is_verified': True,
                    'is_active': True,
                    'national_id': f'EMP-{created_count+1:06d}',
                    'date_of_birth': timezone.now().date() - timedelta(days=365*35),
                    'gender': 'M' if created_count % 2 == 0 else 'F',
                    'county': 'Nairobi'
                }
            )
            if user_created:
                user.set_password('employer123')
                user.save()
                print(f"  ✅ Created employer user: {user.email}")
            
            employer_data['user'] = user
            employer, created = EmployerProfile.objects.get_or_create(
                user=user,
                defaults=employer_data
            )
            if created:
                created_count += 1
                print(f"  ✅ Created employer: {employer.company_name}")
            else:
                # Update existing employer
                for key, value in employer_data.items():
                    if key != 'user' and key != 'country':
                        setattr(employer, key, value)
                employer.save()
                print(f"  🔄 Updated employer: {employer.company_name}")
                
        except Exception as e:
            print(f"  ⚠️ Error creating employer: {e}")
    
    print(f"✅ Loaded {created_count} new employers")
    return created_count


def load_agencies():
    """Load recruitment agencies into the database"""
    from agencies.models import RecruitmentAgency
    from accounts.models import User
    from jobs.models import Country
    
    print("📊 Loading recruitment agencies...")
    
    try:
        kenya = Country.objects.get(code='KE')
        uk = Country.objects.get(code='GB')
        usa = Country.objects.get(code='US')
        canada = Country.objects.get(code='CA')
        australia = Country.objects.get(code='AU')
        uae = Country.objects.get(code='AE')
        germany = Country.objects.get(code='DE')
        south_africa = Country.objects.get(code='ZA')
        nigeria = Country.objects.get(code='NG')
        tanzania = Country.objects.get(code='TZ')
        uganda = Country.objects.get(code='UG')
        rwanda = Country.objects.get(code='RW')
        india = Country.objects.get(code='IN')
        singapore = Country.objects.get(code='SG')
        new_zealand = Country.objects.get(code='NZ')
        switzerland = Country.objects.get(code='CH')
        netherlands = Country.objects.get(code='NL')
        sweden = Country.objects.get(code='SE')
    except Country.DoesNotExist:
        print("  ⚠️ Countries not found, run load_countries first")
        return 0
    
    agencies_data = [
        {
            'agency_name': 'Public Service Commission',
            'registration_number': 'PSC-REG-001',
            'license_number': 'PSC-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+254-20-222-3333',
            'contact_email': 'info@psc.go.ke',
            'address': 'P.O. Box 30095-00100, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'website': 'https://www.psc.go.ke',
            'description': 'Kenya Public Service Commission - Government recruitment agency',
            'specializations': ['Government', 'Administration', 'Public Service']
        },
        {
            'agency_name': 'Kenya Medical Recruitment Agency',
            'registration_number': 'KMRA-REG-001',
            'license_number': 'KMRA-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+254-20-222-4444',
            'contact_email': 'info@kmra.go.ke',
            'address': 'P.O. Box 45678-00100, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'website': 'https://www.kmra.go.ke',
            'description': 'Specialized in healthcare recruitment for local and international positions',
            'specializations': ['Healthcare', 'Medical', 'Nursing']
        },
        {
            'agency_name': 'Global Recruitment Solutions',
            'registration_number': 'GRS-REG-001',
            'license_number': 'GRS-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+254-20-222-5555',
            'contact_email': 'info@globalrecruit.com',
            'address': 'P.O. Box 56789-00100, Nairobi, Kenya',
            'country': kenya,
            'is_verified': True,
            'website': 'https://www.globalrecruit.com',
            'description': 'International recruitment agency for skilled professionals',
            'specializations': ['IT', 'Engineering', 'Finance']
        },
        {
            'agency_name': 'UK Healthcare Recruitment',
            'registration_number': 'UKHR-REG-001',
            'license_number': 'UKHR-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+44-20-222-6666',
            'contact_email': 'info@ukhealthcare.co.uk',
            'address': 'London, United Kingdom',
            'country': uk,
            'is_verified': True,
            'website': 'https://www.ukhealthcare.co.uk',
            'description': 'Recruitment agency specializing in UK healthcare placements',
            'specializations': ['Healthcare', 'Nursing', 'Doctors']
        },
        {
            'agency_name': 'Canada Immigration Recruitment',
            'registration_number': 'CIR-REG-001',
            'license_number': 'CIR-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+1-416-222-7777',
            'contact_email': 'info@canadaimmigration.ca',
            'address': 'Toronto, Canada',
            'country': canada,
            'is_verified': True,
            'website': 'https://www.canadaimmigration.ca',
            'description': 'Specialized in Canadian work visas and job placement',
            'specializations': ['Immigration', 'Skilled Workers', 'Healthcare']
        },
        {
            'agency_name': 'Gulf Recruitment Services',
            'registration_number': 'GRS-REG-002',
            'license_number': 'GRS-LIC-002',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+971-4-222-8888',
            'contact_email': 'info@gulfrecruit.ae',
            'address': 'Dubai, United Arab Emirates',
            'country': uae,
            'is_verified': True,
            'website': 'https://www.gulfrecruit.ae',
            'description': 'Recruitment for Middle East and Gulf countries',
            'specializations': ['Construction', 'Engineering', 'Hospitality']
        },
        {
            'agency_name': 'Australian Skills Recruitment',
            'registration_number': 'ASR-REG-001',
            'license_number': 'ASR-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+61-2-222-9999',
            'contact_email': 'info@australianskills.com.au',
            'address': 'Sydney, Australia',
            'country': australia,
            'is_verified': True,
            'website': 'https://www.australianskills.com.au',
            'description': 'Recruitment for Australian skilled worker programs',
            'specializations': ['IT', 'Engineering', 'Construction']
        },
        {
            'agency_name': 'US Work Solutions',
            'registration_number': 'USWS-REG-001',
            'license_number': 'USWS-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+1-202-222-0000',
            'contact_email': 'info@usworksolutions.com',
            'address': 'Washington DC, USA',
            'country': usa,
            'is_verified': True,
            'website': 'https://www.usworksolutions.com',
            'description': 'Recruitment for US work visas and job placements',
            'specializations': ['Technology', 'Healthcare', 'Finance']
        },
        {
            'agency_name': 'German Technical Recruitment',
            'registration_number': 'GTR-REG-001',
            'license_number': 'GTR-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+49-30-222-1111',
            'contact_email': 'info@germantech.de',
            'address': 'Berlin, Germany',
            'country': germany,
            'is_verified': True,
            'website': 'https://www.germantech.de',
            'description': 'Specialized in technical recruitment for Germany',
            'specializations': ['Engineering', 'Technology', 'Manufacturing']
        },
        {
            'agency_name': 'South African Employment Services',
            'registration_number': 'SAES-REG-001',
            'license_number': 'SAES-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+27-11-222-2222',
            'contact_email': 'info@saes.co.za',
            'address': 'Johannesburg, South Africa',
            'country': south_africa,
            'is_verified': True,
            'website': 'https://www.saes.co.za',
            'description': 'Recruitment for South African and SADC region',
            'specializations': ['Mining', 'Healthcare', 'Education']
        },
        {
            'agency_name': 'Nigerian Federal Civil Service',
            'registration_number': 'NFCS-REG-001',
            'license_number': 'NFCS-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+234-1-222-3333',
            'contact_email': 'info@federalcivilservice.gov.ng',
            'address': 'Abuja, Nigeria',
            'country': nigeria,
            'is_verified': True,
            'website': 'https://www.federalcivilservice.gov.ng',
            'description': 'Nigerian Federal Civil Service Commission',
            'specializations': ['Government', 'Administration', 'Public Service']
        },
        {
            'agency_name': 'Singapore Talent Recruitment',
            'registration_number': 'STR-REG-001',
            'license_number': 'STR-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+65-6222-3333',
            'contact_email': 'info@singaporetalent.sg',
            'address': 'Singapore',
            'country': singapore,
            'is_verified': True,
            'website': 'https://www.singaporetalent.sg',
            'description': 'Recruitment for Singapore skilled worker programs',
            'specializations': ['IT', 'Finance', 'Healthcare']
        },
        {
            'agency_name': 'Swiss International Recruitment',
            'registration_number': 'SIR-REG-001',
            'license_number': 'SIR-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+41-44-222-3333',
            'contact_email': 'info@swissrecruit.ch',
            'address': 'Zurich, Switzerland',
            'country': switzerland,
            'is_verified': True,
            'website': 'https://www.swissrecruit.ch',
            'description': 'Recruitment for Swiss international companies',
            'specializations': ['Finance', 'Technology', 'Healthcare']
        },
        {
            'agency_name': 'Dutch Tech Recruitment',
            'registration_number': 'DTR-REG-001',
            'license_number': 'DTR-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+31-20-222-3333',
            'contact_email': 'info@dutchtech.nl',
            'address': 'Amsterdam, Netherlands',
            'country': netherlands,
            'is_verified': True,
            'website': 'https://www.dutchtech.nl',
            'description': 'Recruitment for Dutch technology sector',
            'specializations': ['IT', 'Engineering', 'Design']
        },
        {
            'agency_name': 'Nordic Recruitment Services',
            'registration_number': 'NRS-REG-001',
            'license_number': 'NRS-LIC-001',
            'license_expiry': timezone.now().date() + timedelta(days=365),
            'contact_phone': '+46-8-222-3333',
            'contact_email': 'info@nordicrecruit.se',
            'address': 'Stockholm, Sweden',
            'country': sweden,
            'is_verified': True,
            'website': 'https://www.nordicrecruit.se',
            'description': 'Recruitment for Nordic region countries',
            'specializations': ['Technology', 'Healthcare', 'Renewable Energy']
        }
    ]
    
    created_count = 0
    for agency_data in agencies_data:
        try:
            email = f"{agency_data['agency_name'].lower().replace(' ', '').replace('&', '').replace('.', '')}@agency.com"
            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': f"{agency_data['agency_name']} Admin",
                    'phone_number': f"0712345{700+created_count:02d}",
                    'user_type': 'agency',
                    'status': 'approved',
                    'is_verified': True,
                    'is_active': True,
                    'national_id': f'AGY-{created_count+1:06d}',
                    'date_of_birth': timezone.now().date() - timedelta(days=365*32),
                    'gender': 'F' if created_count % 2 == 0 else 'M',
                    'county': 'Nairobi'
                }
            )
            if user_created:
                user.set_password('agency123')
                user.save()
                print(f"  ✅ Created agency user: {user.email}")
            
            agency_data['user'] = user
            agency, created = RecruitmentAgency.objects.get_or_create(
                user=user,
                defaults=agency_data
            )
            if created:
                created_count += 1
                print(f"  ✅ Created agency: {agency.agency_name}")
            else:
                # Update existing agency
                for key, value in agency_data.items():
                    if key != 'user' and key != 'country':
                        setattr(agency, key, value)
                agency.save()
                print(f"  🔄 Updated agency: {agency.agency_name}")
                
        except Exception as e:
            print(f"  ⚠️ Error creating agency: {e}")
    
    print(f"✅ Loaded {created_count} new agencies")
    return created_count


def load_sample_jobs():
    """Load sample job listings into the database"""
    from jobs.models import Job, Category, Country
    from agencies.models import RecruitmentAgency
    from employers.models import EmployerProfile
    
    print("📊 Loading sample jobs...")
    
    try:
        categories = {
            'government': Category.objects.get(name='Government & Public Sector'),
            'admin': Category.objects.get(name='Administration'),
            'finance': Category.objects.get(name='Finance & Accounting'),
            'hr': Category.objects.get(name='Human Resources'),
            'it': Category.objects.get(name='Information Technology'),
            'legal': Category.objects.get(name='Legal'),
            'health': Category.objects.get(name='Health & Medical'),
            'education': Category.objects.get(name='Education & Training'),
            'engineering': Category.objects.get(name='Engineering'),
            'hospitality': Category.objects.get(name='Hospitality & Tourism'),
            'construction': Category.objects.get(name='Construction & Building'),
            'sales': Category.objects.get(name='Sales & Marketing'),
            'manufacturing': Category.objects.get(name='Manufacturing & Production'),
            'agriculture': Category.objects.get(name='Agriculture & Farming'),
            'transport': Category.objects.get(name='Transport & Logistics'),
            'security': Category.objects.get(name='Security & Defense'),
            'communications': Category.objects.get(name='Communications & Media'),
            'research': Category.objects.get(name='Research & Development'),
            'customer_service': Category.objects.get(name='Customer Service'),
            'real_estate': Category.objects.get(name='Real Estate & Property')
        }
    except Category.DoesNotExist:
        print("  ⚠️ Categories not found, run load_categories first")
        return 0
    
    try:
        kenya = Country.objects.get(code='KE')
        uk = Country.objects.get(code='GB')
        usa = Country.objects.get(code='US')
        canada = Country.objects.get(code='CA')
        australia = Country.objects.get(code='AU')
        germany = Country.objects.get(code='DE')
        uae = Country.objects.get(code='AE')
        south_africa = Country.objects.get(code='ZA')
        nigeria = Country.objects.get(code='NG')
        tanzania = Country.objects.get(code='TZ')
        uganda = Country.objects.get(code='UG')
        rwanda = Country.objects.get(code='RW')
        singapore = Country.objects.get(code='SG')
        switzerland = Country.objects.get(code='CH')
        netherlands = Country.objects.get(code='NL')
        sweden = Country.objects.get(code='SE')
        new_zealand = Country.objects.get(code='NZ')
    except Country.DoesNotExist:
        print("  ⚠️ Countries not found, run load_countries first")
        return 0
    
    # Get all agencies
    try:
        psc = RecruitmentAgency.objects.get(agency_name='Public Service Commission')
        kmra = RecruitmentAgency.objects.get(agency_name='Kenya Medical Recruitment Agency')
        global_recruit = RecruitmentAgency.objects.get(agency_name='Global Recruitment Solutions')
        uk_healthcare = RecruitmentAgency.objects.get(agency_name='UK Healthcare Recruitment')
        canada_recruit = RecruitmentAgency.objects.get(agency_name='Canada Immigration Recruitment')
        gulf_recruit = RecruitmentAgency.objects.get(agency_name='Gulf Recruitment Services')
        australia_recruit = RecruitmentAgency.objects.get(agency_name='Australian Skills Recruitment')
        us_works = RecruitmentAgency.objects.get(agency_name='US Work Solutions')
        german_tech = RecruitmentAgency.objects.get(agency_name='German Technical Recruitment')
        sa_services = RecruitmentAgency.objects.get(agency_name='South African Employment Services')
        nigeria_fcs = RecruitmentAgency.objects.get(agency_name='Nigerian Federal Civil Service')
        singapore_talent = RecruitmentAgency.objects.get(agency_name='Singapore Talent Recruitment')
        swiss_recruit = RecruitmentAgency.objects.get(agency_name='Swiss International Recruitment')
        dutch_tech = RecruitmentAgency.objects.get(agency_name='Dutch Tech Recruitment')
        nordic_recruit = RecruitmentAgency.objects.get(agency_name='Nordic Recruitment Services')
    except RecruitmentAgency.DoesNotExist:
        print("  ⚠️ Agencies not found, run load_agencies first")
        return 0
    
    # Get employers
    try:
        kcb = EmployerProfile.objects.get(company_name='Kenya Commercial Bank')
        safaricom = EmployerProfile.objects.get(company_name='Safaricom PLC')
        equity = EmployerProfile.objects.get(company_name='Equity Bank Kenya')
        kq = EmployerProfile.objects.get(company_name='Kenya Airways')
        nmg = EmployerProfile.objects.get(company_name='Nation Media Group')
        brookside = EmployerProfile.objects.get(company_name='Brookside Dairy Limited')
        jubilee = EmployerProfile.objects.get(company_name='Jubilee Holdings Limited')
        royal_media = EmployerProfile.objects.get(company_name='Royal Media Services')
        kakuzi = EmployerProfile.objects.get(company_name='Kakuzi PLC')
        bat_kenya = EmployerProfile.objects.get(company_name='British American Tobacco Kenya')
        shell_kenya = EmployerProfile.objects.get(company_name='Shell Kenya Limited')
    except EmployerProfile.DoesNotExist:
        print("  ⚠️ Employers not found, run load_employers first")
        return 0
    
    jobs_data = [
        # === KENYA AGENCY JOBS ===
        {
            'title': 'Senior Administrative Officer - Government',
            'agency': psc,
            'country': kenya,
            'category': categories['admin'],
            'description': 'Lead administrative operations and coordinate government services delivery across multiple departments.',
            'responsibilities': 'Oversee daily operations, manage staff, coordinate with departments, prepare reports, implement policies',
            'requirements': "Bachelor's degree in Public Administration or related field. 5+ years experience in government administration.",
            'benefits': 'Medical cover, Pension scheme, Housing allowance, Car loan facility',
            'salary_min': Decimal('80000'),
            'salary_max': Decimal('120000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship required',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=30),
            'status': 'active',
            'is_featured': True,
            'is_verified': True
        },
        {
            'title': 'Finance Officer - Government Treasury',
            'agency': psc,
            'country': kenya,
            'category': categories['finance'],
            'description': 'Manage financial operations, budgeting, and reporting for government departments.',
            'responsibilities': 'Budget preparation, financial reporting, compliance, audit support, treasury management',
            'requirements': 'CPA(K) or equivalent. 3+ years experience in public finance management.',
            'benefits': 'Medical cover, Pension, Training opportunities, Housing allowance',
            'salary_min': Decimal('60000'),
            'salary_max': Decimal('90000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship required',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=25),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Healthcare Administrator - County Government',
            'agency': kmra,
            'country': kenya,
            'category': categories['health'],
            'description': 'Coordinate healthcare services and administration at county level.',
            'responsibilities': 'Manage healthcare facilities, coordinate medical staff, patient services, quality assurance',
            'requirements': 'Bachelors in Healthcare Administration or Public Health. 3+ years experience.',
            'benefits': 'Medical cover, Pension, Housing allowance, Car allowance',
            'salary_min': Decimal('65000'),
            'salary_max': Decimal('95000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Mombasa, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship required',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=28),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'IT Systems Administrator - Government',
            'agency': global_recruit,
            'country': kenya,
            'category': categories['it'],
            'description': 'Manage and maintain government IT systems, networks, and infrastructure.',
            'responsibilities': 'Network administration, system maintenance, user support, security management, database administration',
            'requirements': 'Degree in Computer Science or IT. 3+ years experience. CCNA, MCSA preferred.',
            'benefits': 'Medical cover, Pension, Training, Certification support, Flexible work',
            'salary_min': Decimal('70000'),
            'salary_max': Decimal('100000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship or valid work permit',
            'required_languages': ['English'],
            'closing_date': timezone.now() + timedelta(days=20),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Human Resources Manager - Public Sector',
            'agency': global_recruit,
            'country': kenya,
            'category': categories['hr'],
            'description': 'Lead HR operations including recruitment, training, performance management, and employee relations.',
            'responsibilities': 'Recruitment, training, performance management, employee relations, policy development, succession planning',
            'requirements': 'Bachelors in HR Management. 5+ years experience. CHRP certification preferred.',
            'benefits': 'Medical cover, Pension, Performance bonuses, Car allowance',
            'salary_min': Decimal('90000'),
            'salary_max': Decimal('130000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship required',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=35),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Legal Counsel - Government',
            'agency': psc,
            'country': kenya,
            'category': categories['legal'],
            'description': 'Provide legal advice and representation for government departments.',
            'responsibilities': 'Legal advisory, contract review, compliance, dispute resolution, legislative drafting',
            'requirements': 'Bachelor of Laws (LLB). 5+ years experience in public law. Advocate of the High Court.',
            'benefits': 'Medical cover, Pension, Housing allowance, Professional development',
            'salary_min': Decimal('100000'),
            'salary_max': Decimal('150000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship required',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=40),
            'status': 'active',
            'is_featured': True,
            'is_verified': True
        },
        
        # === KENYA EMPLOYER JOBS ===
        {
            'title': 'Branch Manager - KCB',
            'employer': kcb,
            'country': kenya,
            'category': categories['finance'],
            'description': 'Lead branch operations and drive business growth for KCB.',
            'responsibilities': 'Manage branch operations, lead team, drive sales, ensure compliance, customer relationship management',
            'requirements': 'Degree in Business or Finance. 5+ years banking experience. CPA or banking certification preferred.',
            'benefits': 'Medical cover, Pension, Performance bonuses, Car allowance, Phone allowance',
            'salary_min': Decimal('120000'),
            'salary_max': Decimal('180000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship required',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=35),
            'status': 'active',
            'is_featured': True,
            'is_verified': True
        },
        {
            'title': 'Network Engineer - Safaricom',
            'employer': safaricom,
            'country': kenya,
            'category': categories['it'],
            'description': 'Design and maintain telecommunications network infrastructure.',
            'responsibilities': 'Network design, maintenance, troubleshooting, capacity planning, security implementation',
            'requirements': 'Degree in Telecommunications or IT. 4+ years experience. CCNA/CCNP preferred.',
            'benefits': 'Medical cover, Pension, Stock options, Training, Phone allowance',
            'salary_min': Decimal('90000'),
            'salary_max': Decimal('130000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship required',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=30),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Relationship Manager - Equity Bank',
            'employer': equity,
            'country': kenya,
            'category': categories['finance'],
            'description': 'Build and maintain relationships with high-value clients.',
            'responsibilities': 'Client relationship management, business development, portfolio management, wealth advisory',
            'requirements': 'Degree in Business or Finance. 4+ years banking experience. CFA or CPA preferred.',
            'benefits': 'Medical cover, Pension, Performance bonuses, Car allowance',
            'salary_min': Decimal('100000'),
            'salary_max': Decimal('150000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship required',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=28),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Pilot - Kenya Airways',
            'employer': kq,
            'country': kenya,
            'category': categories['transport'],
            'description': 'Operate commercial aircraft for Kenya Airways.',
            'responsibilities': 'Flight operations, safety compliance, crew coordination, pre-flight planning',
            'requirements': 'ATPL license. 1000+ hours flying experience. Type rated on Boeing 737/787 preferred.',
            'benefits': 'Medical cover, Pension, Staff travel benefits, Training, Accommodation allowance',
            'salary_min': Decimal('250000'),
            'salary_max': Decimal('400000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Valid license and medical certificate',
            'required_languages': ['English'],
            'closing_date': timezone.now() + timedelta(days=45),
            'status': 'active',
            'is_featured': True,
            'is_verified': True
        },
        {
            'title': 'Digital Marketing Manager - Nation Media Group',
            'employer': nmg,
            'country': kenya,
            'category': categories['sales'],
            'description': 'Lead digital marketing strategy for media group.',
            'responsibilities': 'Digital marketing strategy, content marketing, social media management, analytics, team leadership',
            'requirements': 'Degree in Marketing or Communications. 5+ years digital marketing experience.',
            'benefits': 'Medical cover, Pension, Performance bonuses, Training',
            'salary_min': Decimal('80000'),
            'salary_max': Decimal('120000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship required',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=25),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Production Manager - Brookside Dairy',
            'employer': brookside,
            'country': kenya,
            'category': categories['manufacturing'],
            'description': 'Oversee dairy production operations and quality control.',
            'responsibilities': 'Production planning, quality assurance, team management, supply chain coordination, safety compliance',
            'requirements': 'Degree in Food Science or Manufacturing. 5+ years experience in food processing.',
            'benefits': 'Medical cover, Pension, Performance bonuses, Car allowance',
            'salary_min': Decimal('90000'),
            'salary_max': Decimal('130000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Thika, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship required',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=32),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Insurance Underwriter - Jubilee Holdings',
            'employer': jubilee,
            'country': kenya,
            'category': categories['finance'],
            'description': 'Assess and underwrite insurance risks for corporate clients.',
            'responsibilities': 'Risk assessment, policy underwriting, pricing, claims analysis, client advisory',
            'requirements': 'Degree in Actuarial Science or Finance. 4+ years insurance experience. ACII/FCII preferred.',
            'benefits': 'Medical cover, Pension, Performance bonuses, Training',
            'salary_min': Decimal('70000'),
            'salary_max': Decimal('110000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship required',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=28),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Farm Manager - Kakuzi PLC',
            'employer': kakuzi,
            'country': kenya,
            'category': categories['agriculture'],
            'description': 'Manage large-scale agricultural operations including avocado and tea production.',
            'responsibilities': 'Farm operations, crop management, irrigation, team supervision, budget management',
            'requirements': 'Degree in Agriculture or Agribusiness. 5+ years experience in commercial farming.',
            'benefits': 'Medical cover, Pension, Housing, Transport, Training',
            'salary_min': Decimal('80000'),
            'salary_max': Decimal('120000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Thika, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship required',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=35),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        
        # === INTERNATIONAL AGENCY JOBS ===
        {
            'title': 'Registered Nurse - NHS UK',
            'agency': uk_healthcare,
            'country': uk,
            'category': categories['health'],
            'description': 'Join the UK National Health Service as a registered nurse.',
            'responsibilities': 'Patient care, medication administration, health monitoring, care planning, patient education',
            'requirements': 'Degree in Nursing. NMC registration. IELTS 7.0. 3+ years experience.',
            'benefits': 'NHS pension, 28 days holiday, Training opportunities, Relocation package, Health benefits',
            'salary_min': Decimal('25000'),
            'salary_max': Decimal('35000'),
            'salary_currency': 'GBP',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'London, UK',
            'is_remote': False,
            'visa_requirements': 'Health and Care Worker Visa required',
            'required_languages': ['English'],
            'closing_date': timezone.now() + timedelta(days=45),
            'status': 'active',
            'is_featured': True,
            'is_verified': True
        },
        {
            'title': 'Data Scientist - Tech Firm USA',
            'agency': us_works,
            'country': usa,
            'category': categories['it'],
            'description': 'Analyze big data and develop machine learning models.',
            'responsibilities': 'Data analysis, ML model development, data visualization, reporting, algorithm optimization',
            'requirements': 'Masters in Data Science or related. 5+ years experience. Python, R, SQL, TensorFlow.',
            'benefits': 'Health insurance, 401k matching, Stock options, 25 days holiday, Flexible work',
            'salary_min': Decimal('90000'),
            'salary_max': Decimal('140000'),
            'salary_currency': 'USD',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'New York, USA',
            'is_remote': True,
            'visa_requirements': 'H-1B Visa or Green Card required',
            'required_languages': ['English'],
            'closing_date': timezone.now() + timedelta(days=35),
            'status': 'active',
            'is_featured': True,
            'is_verified': True
        },
        {
            'title': 'Civil Engineer - Canada',
            'agency': canada_recruit,
            'country': canada,
            'category': categories['engineering'],
            'description': 'Lead civil engineering projects for infrastructure development.',
            'responsibilities': 'Project design, site management, team coordination, quality control, client communication',
            'requirements': 'BEng Civil Engineering. PEng designation. 5+ years experience.',
            'benefits': 'Health benefits, RRSP matching, 4 weeks holiday, Professional development',
            'salary_min': Decimal('75000'),
            'salary_max': Decimal('110000'),
            'salary_currency': 'CAD',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Toronto, Canada',
            'is_remote': False,
            'visa_requirements': 'Express Entry or Provincial Nominee Program',
            'required_languages': ['English', 'French'],
            'closing_date': timezone.now() + timedelta(days=32),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'IT Project Manager - Australia',
            'agency': australia_recruit,
            'country': australia,
            'category': categories['it'],
            'description': 'Lead IT projects and teams for enterprise solutions.',
            'responsibilities': 'Project planning, team management, stakeholder communication, delivery, quality assurance',
            'requirements': 'PMP certification. 7+ years experience in IT project management.',
            'benefits': 'Health insurance, Superannuation, 5 weeks holiday, Training budget',
            'salary_min': Decimal('120000'),
            'salary_max': Decimal('160000'),
            'salary_currency': 'AUD',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Sydney, Australia',
            'is_remote': False,
            'visa_requirements': 'Skilled Independent Visa (subclass 189) required',
            'required_languages': ['English'],
            'closing_date': timezone.now() + timedelta(days=30),
            'status': 'active',
            'is_featured': True,
            'is_verified': True
        },
        {
            'title': 'Hospitality Manager - Dubai',
            'agency': gulf_recruit,
            'country': uae,
            'category': categories['hospitality'],
            'description': 'Manage hotel operations and guest services for 5-star property.',
            'responsibilities': 'Hotel operations, guest services, staff management, quality assurance, revenue management',
            'requirements': 'Degree in Hospitality Management. 5+ years experience in luxury hotels.',
            'benefits': 'Tax-free salary, Accommodation, Transport, Medical insurance, Annual flight tickets',
            'salary_min': Decimal('15000'),
            'salary_max': Decimal('25000'),
            'salary_currency': 'AED',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Dubai, UAE',
            'is_remote': False,
            'visa_requirements': 'UAE Employment Visa required',
            'required_languages': ['English', 'Arabic'],
            'closing_date': timezone.now() + timedelta(days=25),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Mechanical Engineer - Germany',
            'agency': german_tech,
            'country': germany,
            'category': categories['engineering'],
            'description': 'Design and develop automotive systems for leading car manufacturer.',
            'responsibilities': 'Product design, testing, quality assurance, project coordination, documentation',
            'requirements': 'Degree in Mechanical Engineering. 4+ years experience in automotive industry.',
            'benefits': 'Company pension, Health insurance, 30 days holiday, Training, Car allowance',
            'salary_min': Decimal('55000'),
            'salary_max': Decimal('75000'),
            'salary_currency': 'EUR',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Berlin, Germany',
            'is_remote': False,
            'visa_requirements': 'German Skilled Worker Visa required',
            'required_languages': ['English', 'German'],
            'closing_date': timezone.now() + timedelta(days=40),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Mining Engineer - South Africa',
            'agency': sa_services,
            'country': south_africa,
            'category': categories['engineering'],
            'description': 'Lead mining operations and resource extraction projects.',
            'responsibilities': 'Mine planning, operations management, safety compliance, team leadership, cost management',
            'requirements': 'Mining Engineering degree. 5+ years experience in mining operations.',
            'benefits': 'Medical aid, Pension, Performance bonuses, Housing allowance',
            'salary_min': Decimal('600000'),
            'salary_max': Decimal('900000'),
            'salary_currency': 'ZAR',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Johannesburg, South Africa',
            'is_remote': False,
            'visa_requirements': 'South African Work Permit required',
            'required_languages': ['English'],
            'closing_date': timezone.now() + timedelta(days=30),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Software Engineer - Singapore',
            'agency': singapore_talent,
            'country': singapore,
            'category': categories['it'],
            'description': 'Develop enterprise software solutions for financial services.',
            'responsibilities': 'Software development, system design, code review, testing, deployment',
            'requirements': 'Degree in Computer Science. 5+ years experience. Java, Spring Boot, Angular.',
            'benefits': 'Medical insurance, CPF, Performance bonuses, Training, Flexible work',
            'salary_min': Decimal('8000'),
            'salary_max': Decimal('12000'),
            'salary_currency': 'SGD',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Singapore',
            'is_remote': False,
            'visa_requirements': 'Employment Pass required',
            'required_languages': ['English'],
            'closing_date': timezone.now() + timedelta(days=30),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Financial Analyst - Switzerland',
            'agency': swiss_recruit,
            'country': switzerland,
            'category': categories['finance'],
            'description': 'Analyze financial data and provide strategic insights for international banking.',
            'responsibilities': 'Financial analysis, investment research, portfolio management, risk assessment, reporting',
            'requirements': 'Degree in Finance or Economics. 5+ years experience. CFA preferred.',
            'benefits': 'Medical insurance, Pension, Performance bonuses, 25 days holiday',
            'salary_min': Decimal('100000'),
            'salary_max': Decimal('150000'),
            'salary_currency': 'CHF',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Zurich, Switzerland',
            'is_remote': False,
            'visa_requirements': 'Swiss Work Visa required',
            'required_languages': ['English', 'German'],
            'closing_date': timezone.now() + timedelta(days=35),
            'status': 'active',
            'is_featured': True,
            'is_verified': True
        },
        {
            'title': 'Cloud Architect - Netherlands',
            'agency': dutch_tech,
            'country': netherlands,
            'category': categories['it'],
            'description': 'Design and implement cloud infrastructure for European clients.',
            'responsibilities': 'Cloud architecture, infrastructure design, security, cost optimization, team leadership',
            'requirements': 'Degree in Computer Science. 7+ years experience. AWS/Azure certifications.',
            'benefits': 'Health insurance, Pension, 30 days holiday, Training budget, Home office allowance',
            'salary_min': Decimal('80000'),
            'salary_max': Decimal('120000'),
            'salary_currency': 'EUR',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Amsterdam, Netherlands',
            'is_remote': True,
            'visa_requirements': 'Highly Skilled Migrant Visa required',
            'required_languages': ['English', 'Dutch'],
            'closing_date': timezone.now() + timedelta(days=30),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Renewable Energy Engineer - Sweden',
            'agency': nordic_recruit,
            'country': sweden,
            'category': categories['engineering'],
            'description': 'Design and implement renewable energy solutions.',
            'responsibilities': 'Project design, energy systems analysis, implementation, compliance, team coordination',
            'requirements': 'Degree in Renewable Energy or Electrical Engineering. 5+ years experience.',
            'benefits': 'Medical insurance, Pension, 30 days holiday, Training, Green energy bonus',
            'salary_min': Decimal('60000'),
            'salary_max': Decimal('90000'),
            'salary_currency': 'SEK',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Stockholm, Sweden',
            'is_remote': False,
            'visa_requirements': 'Swedish Work Permit required',
            'required_languages': ['English', 'Swedish'],
            'closing_date': timezone.now() + timedelta(days=35),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        }
    ]
    
    created_count = 0
    for job_data in jobs_data:
        agency = job_data.pop('agency', None)
        employer = job_data.pop('employer', None)
        category = job_data.pop('category', None)
        country = job_data.pop('country', None)
        
        try:
            # Check if job already exists
            existing_job = Job.objects.filter(
                title=job_data['title'],
                country=country,
                category=category
            ).first()
            
            if existing_job:
                print(f"  ℹ️ Job already exists: {job_data['title']}")
                continue
            
            # Create the job
            job = Job(
                title=job_data['title'],
                agency=agency,
                employer=employer,
                country=country,
                category=category,
                **job_data
            )
            job.save()
            created_count += 1
            source = employer.company_name if employer else agency.agency_name if agency else 'N/A'
            print(f"  ✅ Created job: {job.title} ({source})")
            
        except Exception as e:
            print(f"  ⚠️ Error creating job {job_data['title']}: {e}")
    
    print(f"✅ Loaded {created_count} sample jobs")
    return created_count


def create_superuser():
    """Create admin superuser and test users"""
    from accounts.models import User
    
    print("👤 Creating users...")
    
    # Delete existing users to avoid conflicts
    User.objects.filter(email='admin@admin.com').delete()
    User.objects.filter(email='citizen@example.com').delete()
    User.objects.filter(email='employer@example.com').delete()
    User.objects.filter(email='agency@example.com').delete()
    User.objects.filter(email='citizen2@example.com').delete()
    User.objects.filter(email='employer2@example.com').delete()
    User.objects.filter(email='agency2@example.com').delete()
    
    created_count = 0
    
    try:
        # Create superuser
        admin = User.objects.create_superuser(
            email='admin@admin.com',
            password='admin123',
            full_name='System Administrator',
            phone_number='0712345678',
            user_type='admin',
            status='approved',
            is_verified=True,
            is_active=True,
            national_id='ADMIN-001',
            date_of_birth=timezone.now().date() - timedelta(days=365*35),
            gender='M',
            county='Nairobi'
        )
        created_count += 1
        print("  ✅ Created superuser: admin@admin.com / admin123")
    except Exception as e:
        print(f"  ❌ Failed to create superuser: {e}")
    
    try:
        # Create citizen user 1
        citizen = User.objects.create_user(
            email='citizen@example.com',
            password='citizen123',
            full_name='John Kamau',
            phone_number='0712345679',
            national_id='12345678',
            date_of_birth=timezone.now().date() - timedelta(days=365*25),
            gender='M',
            county='Nairobi',
            user_type='citizen',
            status='approved'
        )
        created_count += 1
        print("  ✅ Created citizen: citizen@example.com / citizen123")
    except Exception as e:
        print(f"  ❌ Failed to create citizen: {e}")
    
    try:
        # Create citizen user 2
        citizen2 = User.objects.create_user(
            email='citizen2@example.com',
            password='citizen123',
            full_name='Mary Wanjiru',
            phone_number='0712345680',
            national_id='87654321',
            date_of_birth=timezone.now().date() - timedelta(days=365*28),
            gender='F',
            county='Kiambu',
            user_type='citizen',
            status='approved'
        )
        created_count += 1
        print("  ✅ Created citizen: citizen2@example.com / citizen123")
    except Exception as e:
        print(f"  ❌ Failed to create citizen2: {e}")
    
    try:
        # Create employer user
        employer = User.objects.create_user(
            email='employer@example.com',
            password='employer123',
            full_name='Jane Muthoni',
            phone_number='0712345681',
            national_id='98765432',
            date_of_birth=timezone.now().date() - timedelta(days=365*32),
            gender='F',
            county='Nairobi',
            user_type='employer',
            status='approved'
        )
        created_count += 1
        print("  ✅ Created employer: employer@example.com / employer123")
    except Exception as e:
        print(f"  ❌ Failed to create employer: {e}")
    
    try:
        # Create agency user
        agency = User.objects.create_user(
            email='agency@example.com',
            password='agency123',
            full_name='David Ochieng',
            phone_number='0712345682',
            national_id='11223344',
            date_of_birth=timezone.now().date() - timedelta(days=365*30),
            gender='M',
            county='Nairobi',
            user_type='agency',
            status='approved'
        )
        created_count += 1
        print("  ✅ Created agency: agency@example.com / agency123")
    except Exception as e:
        print(f"  ❌ Failed to create agency: {e}")
    
    print(f"✅ Created {created_count} users")
    
    # Verify superuser was created
    if User.objects.filter(email='admin@admin.com').exists():
        admin = User.objects.get(email='admin@admin.com')
        print(f"  ✅ Verification: Superuser exists with ID {admin.id}")
    else:
        print("  ❌ Verification: Superuser NOT found in database!")
    
    return created_count


@transaction.atomic
def load_all_data():
    """Load all initial data"""
    print("\n" + "="*60)
    print("🚀 STARTING DATA LOADING")
    print("="*60 + "\n")
    
    try:
        # Load everything in order
        load_countries()
        print()
        load_categories()
        print()
        load_employers()
        print()
        load_agencies()
        print()
        load_sample_jobs()
        print()
        load_payment_plans()
        print()
        create_superuser()
        
        # Final verification
        print("\n" + "="*60)
        print("📊 FINAL VERIFICATION")
        print("="*60)
        
        from jobs.models import Country, Category, Job
        from agencies.models import RecruitmentAgency
        from employers.models import EmployerProfile
        from payments.models import PaymentPlan
        from accounts.models import User
        
        print(f"  ✅ Countries: {Country.objects.count()}")
        print(f"  ✅ Categories: {Category.objects.count()}")
        print(f"  ✅ Employers: {EmployerProfile.objects.count()}")
        print(f"  ✅ Agencies: {RecruitmentAgency.objects.count()}")
        print(f"  ✅ Jobs: {Job.objects.count()}")
        print(f"  ✅ Payment Plans: {PaymentPlan.objects.count()}")
        print(f"  ✅ Users: {User.objects.count()}")
        
        # Check if superuser exists
        if User.objects.filter(email='admin@admin.com').exists():
            admin = User.objects.get(email='admin@admin.com')
            print(f"  ✅ Superuser: {admin.email} (ID: {admin.id})")
        else:
            print("  ❌ Superuser NOT found!")
        
        print("\n" + "="*60)
        print("✅ DATA LOADING COMPLETE!")
        print("="*60)
        print("\n🔑 Login credentials:")
        print("  Admin:     admin@admin.com / admin123")
        print("  Citizen:   citizen@example.com / citizen123")
        print("  Citizen2:  citizen2@example.com / citizen123")
        print("  Employer:  employer@example.com / employer123")
        print("  Agency:    agency@example.com / agency123")
        print("\n📊 Data Summary:")
        print(f"  - {Country.objects.count()} countries")
        print(f"  - {Category.objects.count()} categories")
        print(f"  - {EmployerProfile.objects.count()} employers")
        print(f"  - {RecruitmentAgency.objects.count()} agencies")
        print(f"  - {Job.objects.count()} jobs")
        print(f"  - {PaymentPlan.objects.count()} payment plans")
        print(f"  - {User.objects.count()} users")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error loading data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    load_all_data()