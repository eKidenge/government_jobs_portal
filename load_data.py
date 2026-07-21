# load_data.py
import os
import sys

# ✅ FIX: Add the project root to Python path
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
            'description': 'Apply to 1 job',
            'features': [
                'Apply to 1 job',
                'Valid for 30 days',
                'Access to job details',
                'Application tracking'
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
            'description': 'Full monthly access to all jobs',
            'features': [
                'Unlimited applications',
                'Valid for 30 days',
                'Full job access',
                'Priority support',
                'Application tracking',
                'Email notifications'
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
            'description': 'Three months of full access',
            'features': [
                'Unlimited applications',
                'Valid for 90 days',
                'Full job access',
                'Priority support',
                'Application tracking',
                'Email notifications',
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
            'description': 'Full year of unlimited access',
            'features': [
                'Unlimited applications',
                'Valid for 365 days',
                'Full job access',
                'Priority support',
                'Application tracking',
                'Email notifications',
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
            'description': 'Premium full-year access with extras',
            'features': [
                'Unlimited applications',
                'Valid for 365 days',
                'Full job access',
                'VIP support',
                'Application tracking',
                'Email notifications',
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
            # Update existing plan if needed
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
    
    print("📊 Loading employers...")
    
    # Create employer users first
    employer_users_data = [
        {'email': 'employer1@company.com', 'full_name': 'John Mwangi', 'phone_number': '0712345001', 'password': 'employer123'},
        {'email': 'employer2@company.com', 'full_name': 'Jane Akinyi', 'phone_number': '0712345002', 'password': 'employer123'},
        {'email': 'employer3@company.com', 'full_name': 'Peter Ochieng', 'phone_number': '0712345003', 'password': 'employer123'},
    ]
    
    employers_data = [
        {
            'company_name': 'Kenya Commercial Bank',
            'registration_number': 'KCB/2024/001',
            'industry': 'Banking & Finance',
            'phone_number': '0712345678',
            'address': 'KCB Towers, Nairobi, Kenya',
            'is_verified': True,
            'description': 'Leading commercial bank in East Africa',
            'website': 'https://www.kcb.co.ke'
        },
        {
            'company_name': 'Safaricom PLC',
            'registration_number': 'SAF/2024/002',
            'industry': 'Telecommunications',
            'phone_number': '0712345679',
            'address': 'Safaricom House, Nairobi, Kenya',
            'is_verified': True,
            'description': 'Leading telecommunications company in Kenya',
            'website': 'https://www.safaricom.co.ke'
        },
        {
            'company_name': 'Equity Bank Kenya',
            'registration_number': 'EQT/2024/003',
            'industry': 'Banking & Finance',
            'phone_number': '0712345680',
            'address': 'Equity Centre, Nairobi, Kenya',
            'is_verified': True,
            'description': 'Leading financial services provider',
            'website': 'https://www.equitybank.co.ke'
        },
        {
            'company_name': 'Kenya Airways',
            'registration_number': 'KQ/2024/004',
            'industry': 'Aviation & Transport',
            'phone_number': '0712345681',
            'address': 'Embakasi, Nairobi, Kenya',
            'is_verified': True,
            'description': 'Flag carrier airline of Kenya',
            'website': 'https://www.kenya-airways.com'
        },
        {
            'company_name': 'Nation Media Group',
            'registration_number': 'NMG/2024/005',
            'industry': 'Media & Communications',
            'phone_number': '0712345682',
            'address': 'Nation Centre, Nairobi, Kenya',
            'is_verified': True,
            'description': 'Leading media house in East Africa',
            'website': 'https://www.nationmedia.com'
        },
    ]
    
    created_count = 0
    for i, employer_data in enumerate(employers_data):
        try:
            # Get or create user for employer
            user_data = employer_users_data[i] if i < len(employer_users_data) else employer_users_data[0]
            
            user, user_created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'full_name': user_data['full_name'],
                    'phone_number': user_data['phone_number'],
                    'user_type': 'employer',
                    'status': 'approved',
                    'is_verified': True,
                    'is_active': True,
                    'national_id': f'EMP-{i+1:06d}',
                    'date_of_birth': timezone.now().date() - timedelta(days=365*30),
                    'gender': 'M' if i % 2 == 0 else 'F',
                    'county': 'Nairobi'
                }
            )
            if user_created:
                user.set_password(user_data['password'])
                user.save()
                print(f"  ✅ Created employer user: {user.email}")
            
            # Create employer profile
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
    
    # Get countries
    try:
        kenya = Country.objects.get(code='KE')
        uk = Country.objects.get(code='GB')
        usa = Country.objects.get(code='US')
        canada = Country.objects.get(code='CA')
        australia = Country.objects.get(code='AU')
        uae = Country.objects.get(code='AE')
        germany = Country.objects.get(code='DE')
        south_africa = Country.objects.get(code='ZA')
    except Country.DoesNotExist:
        print("  ⚠️ Countries not found, run load_countries first")
        return 0
    
    # Agency users
    agency_users_data = [
        {'email': 'psc@go.ke', 'full_name': 'Public Service Commission Admin', 'phone_number': '0712346001', 'password': 'agency123'},
        {'email': 'kmra@go.ke', 'full_name': 'KMRA Admin', 'phone_number': '0712346002', 'password': 'agency123'},
        {'email': 'globalrecruit@global.com', 'full_name': 'Global Recruitment Admin', 'phone_number': '0712346003', 'password': 'agency123'},
        {'email': 'ukhealthcare@nhs.co.uk', 'full_name': 'UK Healthcare Admin', 'phone_number': '0712346004', 'password': 'agency123'},
        {'email': 'canadaimm@ca.com', 'full_name': 'Canada Immigration Admin', 'phone_number': '0712346005', 'password': 'agency123'},
        {'email': 'gulfrecruit@ae.com', 'full_name': 'Gulf Recruitment Admin', 'phone_number': '0712346006', 'password': 'agency123'},
        {'email': 'austskills@au.com', 'full_name': 'Australian Skills Admin', 'phone_number': '0712346007', 'password': 'agency123'},
        {'email': 'usworks@us.com', 'full_name': 'US Work Solutions Admin', 'phone_number': '0712346008', 'password': 'agency123'},
        {'email': 'germantech@de.com', 'full_name': 'German Technical Admin', 'phone_number': '0712346009', 'password': 'agency123'},
        {'email': 'saes@co.za', 'full_name': 'SA Employment Services Admin', 'phone_number': '0712346010', 'password': 'agency123'},
    ]
    
    agencies_data = [
        {
            'agency_name': 'Public Service Commission',
            'license_number': 'PSC/2024/001',
            'phone_number': '+254-20-222-3333',
            'agency_email': 'info@psc.go.ke',
            'address': 'P.O. Box 30095-00100, Nairobi, Kenya',
            'services': 'Government recruitment, Public service placements, Career guidance',
            'is_verified': True,
            'country': kenya,
            'website': 'https://www.psc.go.ke',
            'description': 'Kenya Public Service Commission - Government recruitment agency'
        },
        {
            'agency_name': 'Kenya Medical Recruitment Agency',
            'license_number': 'KMRA/2024/001',
            'phone_number': '+254-20-222-4444',
            'agency_email': 'info@kmra.go.ke',
            'address': 'P.O. Box 45678-00100, Nairobi, Kenya',
            'services': 'Healthcare recruitment, Medical placements, Nursing recruitment',
            'is_verified': True,
            'country': kenya,
            'website': 'https://www.kmra.go.ke',
            'description': 'Specialized in healthcare recruitment for local and international positions'
        },
        {
            'agency_name': 'Global Recruitment Solutions',
            'license_number': 'GRS/2024/001',
            'phone_number': '+254-20-222-5555',
            'agency_email': 'info@globalrecruit.com',
            'address': 'P.O. Box 56789-00100, Nairobi, Kenya',
            'services': 'International recruitment, Skilled professionals, Executive search',
            'is_verified': True,
            'country': kenya,
            'website': 'https://www.globalrecruit.com',
            'description': 'International recruitment agency for skilled professionals'
        },
        {
            'agency_name': 'UK Healthcare Recruitment',
            'license_number': 'UKHR/2024/001',
            'phone_number': '+44-20-222-6666',
            'agency_email': 'info@ukhealthcare.co.uk',
            'address': 'London, United Kingdom',
            'services': 'NHS recruitment, Healthcare placements, Nursing recruitment',
            'is_verified': True,
            'country': uk,
            'website': 'https://www.ukhealthcare.co.uk',
            'description': 'Recruitment agency specializing in UK healthcare placements'
        },
        {
            'agency_name': 'Canada Immigration Recruitment',
            'license_number': 'CIR/2024/001',
            'phone_number': '+1-416-222-7777',
            'agency_email': 'info@canadaimmigration.ca',
            'address': 'Toronto, Canada',
            'services': 'Canadian work visas, Job placement, Immigration services',
            'is_verified': True,
            'country': canada,
            'website': 'https://www.canadaimmigration.ca',
            'description': 'Specialized in Canadian work visas and job placement'
        },
        {
            'agency_name': 'Gulf Recruitment Services',
            'license_number': 'GRS/2024/002',
            'phone_number': '+971-4-222-8888',
            'agency_email': 'info@gulfrecruit.ae',
            'address': 'Dubai, United Arab Emirates',
            'services': 'Gulf country recruitment, Construction, Engineering, Hospitality',
            'is_verified': True,
            'country': uae,
            'website': 'https://www.gulfrecruit.ae',
            'description': 'Recruitment for Middle East and Gulf countries'
        },
        {
            'agency_name': 'Australian Skills Recruitment',
            'license_number': 'ASR/2024/001',
            'phone_number': '+61-2-222-9999',
            'agency_email': 'info@australianskills.com.au',
            'address': 'Sydney, Australia',
            'services': 'Skilled worker programs, IT recruitment, Engineering placements',
            'is_verified': True,
            'country': australia,
            'website': 'https://www.australianskills.com.au',
            'description': 'Recruitment for Australian skilled worker programs'
        },
        {
            'agency_name': 'US Work Solutions',
            'license_number': 'USWS/2024/001',
            'phone_number': '+1-202-222-0000',
            'agency_email': 'info@usworksolutions.com',
            'address': 'Washington DC, USA',
            'services': 'US work visas, Technology recruitment, Healthcare placements',
            'is_verified': True,
            'country': usa,
            'website': 'https://www.usworksolutions.com',
            'description': 'Recruitment for US work visas and job placements'
        },
        {
            'agency_name': 'German Technical Recruitment',
            'license_number': 'GTR/2024/001',
            'phone_number': '+49-30-222-1111',
            'agency_email': 'info@germantech.de',
            'address': 'Berlin, Germany',
            'services': 'Technical recruitment, Engineering, Technology, Manufacturing',
            'is_verified': True,
            'country': germany,
            'website': 'https://www.germantech.de',
            'description': 'Specialized in technical recruitment for Germany'
        },
        {
            'agency_name': 'South African Employment Services',
            'license_number': 'SAES/2024/001',
            'phone_number': '+27-11-222-2222',
            'agency_email': 'info@saes.co.za',
            'address': 'Johannesburg, South Africa',
            'services': 'SADC region recruitment, Mining, Healthcare, Education',
            'is_verified': True,
            'country': south_africa,
            'website': 'https://www.saes.co.za',
            'description': 'Recruitment for South African and SADC region'
        }
    ]
    
    created_count = 0
    for i, agency_data in enumerate(agencies_data):
        try:
            # Get or create user for agency
            user_data = agency_users_data[i] if i < len(agency_users_data) else agency_users_data[0]
            
            user, user_created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'full_name': user_data['full_name'],
                    'phone_number': user_data['phone_number'],
                    'user_type': 'agency',
                    'status': 'approved',
                    'is_verified': True,
                    'is_active': True,
                    'national_id': f'AGY-{i+1:06d}',
                    'date_of_birth': timezone.now().date() - timedelta(days=365*30),
                    'gender': 'M' if i % 2 == 0 else 'F',
                    'county': 'Nairobi'
                }
            )
            if user_created:
                user.set_password(user_data['password'])
                user.save()
                print(f"  ✅ Created agency user: {user.email}")
            
            # Create agency
            agency, created = RecruitmentAgency.objects.get_or_create(
                user=user,
                defaults=agency_data
            )
            if created:
                created_count += 1
                print(f"  ✅ Created agency: {agency.agency_name}")
            else:
                print(f"  ℹ️ Agency already exists: {agency.agency_name}")
                
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
    
    # Get categories
    try:
        government_category = Category.objects.get(name='Government & Public Sector')
        admin_category = Category.objects.get(name='Administration')
        finance_category = Category.objects.get(name='Finance & Accounting')
        hr_category = Category.objects.get(name='Human Resources')
        it_category = Category.objects.get(name='Information Technology')
        legal_category = Category.objects.get(name='Legal')
        health_category = Category.objects.get(name='Health & Medical')
        education_category = Category.objects.get(name='Education & Training')
        engineering_category = Category.objects.get(name='Engineering')
        hospitality_category = Category.objects.get(name='Hospitality & Tourism')
        construction_category = Category.objects.get(name='Construction & Building')
    except Category.DoesNotExist:
        print("  ⚠️ Categories not found, run load_categories first")
        return 0
    
    # Get countries
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
    except Country.DoesNotExist:
        print("  ⚠️ Countries not found, run load_countries first")
        return 0
    
    # Get agencies and employers
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
    except EmployerProfile.DoesNotExist:
        print("  ⚠️ Employers not found, run load_employers first")
        return 0
    
    jobs_data = [
        # Kenya Jobs - Agency
        {
            'title': 'Senior Administrative Officer',
            'agency': psc,
            'country': kenya,
            'category': admin_category,
            'description': 'Lead administrative operations and coordinate government services delivery across multiple departments.',
            'responsibilities': 'Oversee daily operations, manage staff, coordinate with departments, prepare reports',
            'requirements': "Bachelor's degree in Public Administration or related field. 5+ years experience.",
            'benefits': 'Medical cover, Pension scheme, Housing allowance',
            'salary_min': Decimal('80000'),
            'salary_max': Decimal('120000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship or valid work permit',
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
            'category': finance_category,
            'description': 'Manage financial operations, budgeting, and reporting for government departments.',
            'responsibilities': 'Budget preparation, financial reporting, compliance, audit support',
            'requirements': 'CPA(K) or equivalent. 3+ years experience in public finance.',
            'benefits': 'Medical cover, Pension, Training opportunities',
            'salary_min': Decimal('60000'),
            'salary_max': Decimal('90000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship',
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
            'category': health_category,
            'description': 'Coordinate healthcare services and administration at county level.',
            'responsibilities': 'Manage healthcare facilities, coordinate medical staff, patient services',
            'requirements': 'Bachelors in Healthcare Administration or Public Health. 3+ years experience.',
            'benefits': 'Medical cover, Pension, Housing allowance',
            'salary_min': Decimal('65000'),
            'salary_max': Decimal('95000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Mombasa, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=28),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'IT Systems Administrator',
            'agency': global_recruit,
            'country': kenya,
            'category': it_category,
            'description': 'Manage and maintain government IT systems, networks, and infrastructure.',
            'responsibilities': 'Network administration, system maintenance, user support, security management',
            'requirements': 'Degree in Computer Science or IT. 3+ years experience. CCNA, MCSA preferred.',
            'benefits': 'Medical cover, Pension, Training, Certification support',
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
        # Kenya Jobs - Employers
        {
            'title': 'Branch Manager - KCB',
            'employer': kcb,
            'country': kenya,
            'category': finance_category,
            'description': 'Lead branch operations and drive business growth for KCB.',
            'responsibilities': 'Manage branch operations, lead team, drive sales, ensure compliance',
            'requirements': 'Degree in Business or Finance. 5+ years banking experience. CPA preferred.',
            'benefits': 'Medical cover, Pension, Performance bonuses, Car allowance',
            'salary_min': Decimal('120000'),
            'salary_max': Decimal('180000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship',
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
            'category': it_category,
            'description': 'Design and maintain telecommunications network infrastructure.',
            'responsibilities': 'Network design, maintenance, troubleshooting, capacity planning',
            'requirements': 'Degree in Telecommunications or IT. 4+ years experience. CCNA/CCNP preferred.',
            'benefits': 'Medical cover, Pension, Stock options, Training',
            'salary_min': Decimal('90000'),
            'salary_max': Decimal('130000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship',
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
            'category': finance_category,
            'description': 'Build and maintain relationships with high-value clients.',
            'responsibilities': 'Client relationship management, business development, portfolio management',
            'requirements': 'Degree in Business or Finance. 4+ years banking experience.',
            'benefits': 'Medical cover, Pension, Performance bonuses',
            'salary_min': Decimal('100000'),
            'salary_max': Decimal('150000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=28),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Flight Operations Manager - Kenya Airways',
            'employer': kq,
            'country': kenya,
            'category': transport_category,
            'description': 'Manage flight operations and ensure safety compliance.',
            'responsibilities': 'Flight scheduling, crew management, safety oversight, regulatory compliance',
            'requirements': 'Degree in Aviation Management or related. 5+ years experience.',
            'benefits': 'Medical cover, Pension, Flight benefits, Training',
            'salary_min': Decimal('150000'),
            'salary_max': Decimal('200000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=40),
            'status': 'active',
            'is_featured': True,
            'is_verified': True
        },
        # International Jobs - Agencies
        {
            'title': 'Registered Nurse - NHS',
            'agency': uk_healthcare,
            'country': uk,
            'category': health_category,
            'description': 'Join the UK National Health Service as a registered nurse.',
            'responsibilities': 'Patient care, medication administration, health monitoring, care planning',
            'requirements': 'Degree in Nursing. NMC registration. IELTS 7.0. 3+ years experience.',
            'benefits': 'NHS pension, 28 days holiday, Training opportunities, Relocation package',
            'salary_min': Decimal('25000'),
            'salary_max': Decimal('35000'),
            'salary_currency': 'GBP',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'London, UK',
            'is_remote': False,
            'visa_requirements': 'Health and Care Worker Visa',
            'required_languages': ['English'],
            'closing_date': timezone.now() + timedelta(days=45),
            'status': 'active',
            'is_featured': True,
            'is_verified': True
        },
        {
            'title': 'Data Scientist - Tech Firm',
            'agency': us_works,
            'country': usa,
            'category': it_category,
            'description': 'Analyze big data and develop machine learning models.',
            'responsibilities': 'Data analysis, ML model development, data visualization, reporting',
            'requirements': 'Masters in Data Science or related. 5+ years experience. Python, R, SQL.',
            'benefits': 'Health insurance, 401k, Stock options, 25 days holiday',
            'salary_min': Decimal('90000'),
            'salary_max': Decimal('140000'),
            'salary_currency': 'USD',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'New York, USA',
            'is_remote': True,
            'visa_requirements': 'H-1B Visa or Green Card',
            'required_languages': ['English'],
            'closing_date': timezone.now() + timedelta(days=35),
            'status': 'active',
            'is_featured': True,
            'is_verified': True
        },
        {
            'title': 'Civil Engineer - Construction',
            'agency': canada_recruit,
            'country': canada,
            'category': engineering_category,
            'description': 'Lead civil engineering projects for infrastructure development.',
            'responsibilities': 'Project design, site management, team coordination, quality control',
            'requirements': 'BEng Civil Engineering. PEng designation. 5+ years experience.',
            'benefits': 'Health benefits, RRSP, 4 weeks holiday',
            'salary_min': Decimal('75000'),
            'salary_max': Decimal('110000'),
            'salary_currency': 'CAD',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Toronto, Canada',
            'is_remote': False,
            'visa_requirements': 'Express Entry',
            'required_languages': ['English', 'French'],
            'closing_date': timezone.now() + timedelta(days=32),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'IT Project Manager',
            'agency': australia_recruit,
            'country': australia,
            'category': it_category,
            'description': 'Lead IT projects and teams for enterprise solutions.',
            'responsibilities': 'Project planning, team management, stakeholder communication, delivery',
            'requirements': 'PMP certification. 7+ years experience in IT project management.',
            'benefits': 'Health insurance, Superannuation, 5 weeks holiday',
            'salary_min': Decimal('120000'),
            'salary_max': Decimal('160000'),
            'salary_currency': 'AUD',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Sydney, Australia',
            'is_remote': False,
            'visa_requirements': 'Skilled Independent Visa (subclass 189)',
            'required_languages': ['English'],
            'closing_date': timezone.now() + timedelta(days=30),
            'status': 'active',
            'is_featured': True,
            'is_verified': True
        },
        {
            'title': 'Hospitality Manager - Hotel Chain',
            'agency': gulf_recruit,
            'country': uae,
            'category': hospitality_category,
            'description': 'Manage hotel operations and guest services for 5-star property.',
            'responsibilities': 'Hotel operations, guest services, staff management, quality assurance',
            'requirements': 'Degree in Hospitality Management. 5+ years experience in luxury hotels.',
            'benefits': 'Tax-free salary, Accommodation, Transport, Medical insurance',
            'salary_min': Decimal('15000'),
            'salary_max': Decimal('25000'),
            'salary_currency': 'AED',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Dubai, UAE',
            'is_remote': False,
            'visa_requirements': 'UAE Employment Visa',
            'required_languages': ['English', 'Arabic'],
            'closing_date': timezone.now() + timedelta(days=25),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Mechanical Engineer - Automotive',
            'agency': german_tech,
            'country': germany,
            'category': engineering_category,
            'description': 'Design and develop automotive systems for leading car manufacturer.',
            'responsibilities': 'Product design, testing, quality assurance, project coordination',
            'requirements': 'Degree in Mechanical Engineering. 4+ years experience in automotive industry.',
            'benefits': 'Company pension, Health insurance, 30 days holiday, Training',
            'salary_min': Decimal('55000'),
            'salary_max': Decimal('75000'),
            'salary_currency': 'EUR',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Berlin, Germany',
            'is_remote': False,
            'visa_requirements': 'German Skilled Worker Visa',
            'required_languages': ['English', 'German'],
            'closing_date': timezone.now() + timedelta(days=40),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Mining Engineer',
            'agency': sa_services,
            'country': south_africa,
            'category': engineering_category,
            'description': 'Lead mining operations and resource extraction projects.',
            'responsibilities': 'Mine planning, operations management, safety compliance, team leadership',
            'requirements': 'Mining Engineering degree. 5+ years experience in mining.',
            'benefits': 'Medical aid, Pension, Performance bonuses',
            'salary_min': Decimal('600000'),
            'salary_max': Decimal('900000'),
            'salary_currency': 'ZAR',
            'is_salary_negotiable': True,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Johannesburg, South Africa',
            'is_remote': False,
            'visa_requirements': 'South African Work Permit',
            'required_languages': ['English'],
            'closing_date': timezone.now() + timedelta(days=30),
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
        
        # Create the job
        try:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                employer=employer,
                agency=agency,
                country=country,
                category=category,
                defaults=job_data
            )
            if created:
                created_count += 1
                source = employer.company_name if employer else agency.agency_name if agency else 'N/A'
                print(f"  ✅ Created job: {job.title} ({source})")
            else:
                print(f"  ℹ️ Job already exists: {job.title}")
        except Exception as e:
            print(f"  ⚠️ Error creating job: {e}")
    
    print(f"✅ Loaded {created_count} sample jobs")
    return created_count


def create_superuser():
    """Create admin superuser if it doesn't exist"""
    from accounts.models import User
    
    print("👤 Checking superuser...")
    
    # Delete existing admin if exists to avoid conflicts
    User.objects.filter(email='admin@admin.com').delete()
    
    try:
        # Create superuser using the custom UserManager
        admin = User.objects.create_superuser(
            email='admin@admin.com',
            password='admin123'
        )
        print("  ✅ Created superuser: admin@admin.com / admin123")
        print(f"  📋 User ID: {admin.id}")
        print(f"  📋 Is Staff: {admin.is_staff}")
        print(f"  📋 Is Superuser: {admin.is_superuser}")
    except Exception as e:
        print(f"  ❌ Failed to create superuser: {e}")
        # Try alternative method if first fails
        try:
            admin = User.objects.create_user(
                email='admin@admin.com',
                password='admin123',
                is_staff=True,
                is_superuser=True,
                user_type='admin',
                status='approved'
            )
            print("  ✅ Created superuser (alternative method): admin@admin.com / admin123")
        except Exception as e2:
            print(f"  ❌ Alternative method also failed: {e2}")
    
    # Create test users
    # Citizen
    User.objects.filter(email='citizen@example.com').delete()
    try:
        citizen = User.objects.create_user(
            email='citizen@example.com',
            password='citizen123',
            full_name='Test Citizen',
            phone_number='0712345678',
            national_id='12345678',
            date_of_birth=timezone.now().date() - timedelta(days=365*25),
            gender='M',
            county='Nairobi',
            user_type='citizen',
            status='approved'
        )
        print("  ✅ Created citizen user: citizen@example.com / citizen123")
    except Exception as e:
        print(f"  ❌ Failed to create citizen user: {e}")
    
    # Employer user
    User.objects.filter(email='employer@example.com').delete()
    try:
        employer = User.objects.create_user(
            email='employer@example.com',
            password='employer123',
            full_name='Test Employer',
            phone_number='0712345679',
            national_id='87654321',
            date_of_birth=timezone.now().date() - timedelta(days=365*30),
            gender='M',
            county='Nairobi',
            user_type='employer',
            status='approved'
        )
        print("  ✅ Created employer user: employer@example.com / employer123")
    except Exception as e:
        print(f"  ❌ Failed to create employer user: {e}")
    
    # Verify superuser was created
    if User.objects.filter(email='admin@admin.com').exists():
        admin = User.objects.get(email='admin@admin.com')
        print(f"  ✅ Verification: Superuser exists with ID {admin.id}")
        print(f"  ✅ Can login with: admin@admin.com / admin123")
    else:
        print("  ❌ Verification: Superuser NOT found in database!")


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
        
        # Check if data loaded correctly
        from jobs.models import Country, Category, Job
        from agencies.models import RecruitmentAgency
        from employers.models import EmployerProfile
        from payments.models import PaymentPlan
        
        print(f"  ✅ Countries: {Country.objects.count()}")
        print(f"  ✅ Categories: {Category.objects.count()}")
        print(f"  ✅ Employers: {EmployerProfile.objects.count()}")
        print(f"  ✅ Agencies: {RecruitmentAgency.objects.count()}")
        print(f"  ✅ Jobs: {Job.objects.count()}")
        print(f"  ✅ Payment Plans: {PaymentPlan.objects.count()}")
        
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
        print("  Employer:  employer@example.com / employer123")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error loading data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    load_all_data()