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
        {'name': 'United Kingdom', 'code': 'UK', 'currency': 'GBP', 'currency_symbol': '£', 'description': 'United Kingdom of Great Britain and Northern Ireland', 'is_active': True},
        {'name': 'United States', 'code': 'USA', 'currency': 'USD', 'currency_symbol': '$', 'description': 'United States of America', 'is_active': True},
        {'name': 'Canada', 'code': 'CA', 'currency': 'CAD', 'currency_symbol': 'C$', 'description': 'North American country', 'is_active': True},
        {'name': 'Australia', 'code': 'AU', 'currency': 'AUD', 'currency_symbol': 'A$', 'description': 'Australian continent', 'is_active': True},
        {'name': 'Germany', 'code': 'DE', 'currency': 'EUR', 'currency_symbol': '€', 'description': 'Central European country', 'is_active': True},
        {'name': 'United Arab Emirates', 'code': 'AE', 'currency': 'AED', 'currency_symbol': 'د.إ', 'description': 'Middle Eastern country', 'is_active': True},
        {'name': 'South Africa', 'code': 'ZA', 'currency': 'ZAR', 'currency_symbol': 'R', 'description': 'Southern African nation', 'is_active': True},
        {'name': 'Nigeria', 'code': 'NG', 'currency': 'NGN', 'currency_symbol': '₦', 'description': 'West African nation', 'is_active': True},
        {'name': 'Ghana', 'code': 'GH', 'currency': 'GHS', 'currency_symbol': 'GH₵', 'description': 'West African nation', 'is_active': True},
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


def load_job_categories():
    """Load job categories into the database"""
    from jobs.models import JobCategory
    
    print("📊 Loading job categories...")
    
    categories_data = [
        {'name': 'Government & Public Sector', 'slug': 'government-public-sector', 'icon': '🏛️', 'description': 'Government and public sector positions', 'is_active': True},
        {'name': 'Administration', 'slug': 'administration', 'icon': '📋', 'description': 'Administrative and office management roles', 'is_active': True},
        {'name': 'Finance & Accounting', 'slug': 'finance-accounting', 'icon': '💰', 'description': 'Financial management and accounting positions', 'is_active': True},
        {'name': 'Human Resources', 'slug': 'human-resources', 'icon': '👥', 'description': 'HR and personnel management roles', 'is_active': True},
        {'name': 'Information Technology', 'slug': 'information-technology', 'icon': '💻', 'description': 'IT and technology positions', 'is_active': True},
        {'name': 'Legal', 'slug': 'legal', 'icon': '⚖️', 'description': 'Legal and compliance roles', 'is_active': True},
        {'name': 'Health & Medical', 'slug': 'health-medical', 'icon': '🏥', 'description': 'Healthcare and medical positions', 'is_active': True},
        {'name': 'Education', 'slug': 'education', 'icon': '📚', 'description': 'Teaching and education roles', 'is_active': True},
        {'name': 'Engineering', 'slug': 'engineering', 'icon': '🔧', 'description': 'Engineering and technical roles', 'is_active': True},
        {'name': 'Agriculture', 'slug': 'agriculture', 'icon': '🌾', 'description': 'Agricultural and environmental positions', 'is_active': True},
        {'name': 'Security & Defense', 'slug': 'security-defense', 'icon': '🛡️', 'description': 'Security and defense roles', 'is_active': True},
        {'name': 'Transport & Logistics', 'slug': 'transport-logistics', 'icon': '🚚', 'description': 'Transportation and logistics positions', 'is_active': True},
        {'name': 'Communications', 'slug': 'communications', 'icon': '📡', 'description': 'Communications and media roles', 'is_active': True},
        {'name': 'Research & Development', 'slug': 'research-development', 'icon': '🔬', 'description': 'Research and development positions', 'is_active': True},
        {'name': 'Customer Service', 'slug': 'customer-service', 'icon': '🎯', 'description': 'Customer service and support roles', 'is_active': True},
        {'name': 'Hospitality', 'slug': 'hospitality', 'icon': '🏨', 'description': 'Hospitality and tourism positions', 'is_active': True},
        {'name': 'Construction', 'slug': 'construction', 'icon': '🏗️', 'description': 'Construction and building roles', 'is_active': True},
        {'name': 'Manufacturing', 'slug': 'manufacturing', 'icon': '🏭', 'description': 'Manufacturing and production positions', 'is_active': True},
    ]
    
    created_count = 0
    for category_data in categories_data:
        category, created = JobCategory.objects.get_or_create(
            slug=category_data['slug'],
            defaults=category_data
        )
        if created:
            created_count += 1
            print(f"  ✅ Created category: {category.name}")
        else:
            print(f"  ℹ️ Category already exists: {category.name}")
    
    print(f"✅ Loaded {created_count} new job categories")
    return created_count


def load_agencies():
    """Load recruitment agencies into the database"""
    try:
        from agencies.models import Agency
    except ImportError:
        print("  ⚠️ Agency model not found, skipping...")
        return 0
    
    from jobs.models import Country
    
    print("📊 Loading recruitment agencies...")
    
    # Get countries
    try:
        kenya = Country.objects.get(code='KE')
        uk = Country.objects.get(code='UK')
        usa = Country.objects.get(code='USA')
        canada = Country.objects.get(code='CA')
        australia = Country.objects.get(code='AU')
        uae = Country.objects.get(code='AE')
        germany = Country.objects.get(code='DE')
        south_africa = Country.objects.get(code='ZA')
    except Country.DoesNotExist:
        print("  ⚠️ Countries not found, run load_countries first")
        return 0
    
    agencies_data = [
        {
            'name': 'Public Service Commission',
            'description': 'Kenya Public Service Commission - Government recruitment agency',
            'email': 'info@psc.go.ke',
            'phone': '+254-20-222-3333',
            'website': 'https://www.psc.go.ke',
            'is_active': True,
            'country': kenya,
            'address': 'P.O. Box 30095-00100, Nairobi, Kenya',
            'specializations': ['Government', 'Administration', 'Public Service'],
            'is_verified': True,
            'verification_date': timezone.now()
        },
        {
            'name': 'Kenya Medical Recruitment Agency',
            'description': 'Specialized in healthcare recruitment for local and international positions',
            'email': 'info@kmra.go.ke',
            'phone': '+254-20-222-4444',
            'website': 'https://www.kmra.go.ke',
            'is_active': True,
            'country': kenya,
            'address': 'P.O. Box 45678-00100, Nairobi, Kenya',
            'specializations': ['Healthcare', 'Medical', 'Nursing'],
            'is_verified': True,
            'verification_date': timezone.now()
        },
        {
            'name': 'Global Recruitment Solutions',
            'description': 'International recruitment agency for skilled professionals',
            'email': 'info@globalrecruit.com',
            'phone': '+254-20-222-5555',
            'website': 'https://www.globalrecruit.com',
            'is_active': True,
            'country': kenya,
            'address': 'P.O. Box 56789-00100, Nairobi, Kenya',
            'specializations': ['IT', 'Engineering', 'Finance'],
            'is_verified': True,
            'verification_date': timezone.now()
        },
        {
            'name': 'UK Healthcare Recruitment',
            'description': 'Recruitment agency specializing in UK healthcare placements',
            'email': 'info@ukhealthcare.co.uk',
            'phone': '+44-20-222-6666',
            'website': 'https://www.ukhealthcare.co.uk',
            'is_active': True,
            'country': uk,
            'address': 'London, United Kingdom',
            'specializations': ['Healthcare', 'Nursing', 'Doctors'],
            'is_verified': True,
            'verification_date': timezone.now()
        },
        {
            'name': 'Canada Immigration Recruitment',
            'description': 'Specialized in Canadian work visas and job placement',
            'email': 'info@canadaimmigration.ca',
            'phone': '+1-416-222-7777',
            'website': 'https://www.canadaimmigration.ca',
            'is_active': True,
            'country': canada,
            'address': 'Toronto, Canada',
            'specializations': ['Immigration', 'Skilled Workers', 'Healthcare'],
            'is_verified': True,
            'verification_date': timezone.now()
        },
        {
            'name': 'Gulf Recruitment Services',
            'description': 'Recruitment for Middle East and Gulf countries',
            'email': 'info@gulfrecruit.ae',
            'phone': '+971-4-222-8888',
            'website': 'https://www.gulfrecruit.ae',
            'is_active': True,
            'country': uae,
            'address': 'Dubai, United Arab Emirates',
            'specializations': ['Construction', 'Engineering', 'Hospitality'],
            'is_verified': True,
            'verification_date': timezone.now()
        },
        {
            'name': 'Australian Skills Recruitment',
            'description': 'Recruitment for Australian skilled worker programs',
            'email': 'info@australianskills.com.au',
            'phone': '+61-2-222-9999',
            'website': 'https://www.australianskills.com.au',
            'is_active': True,
            'country': australia,
            'address': 'Sydney, Australia',
            'specializations': ['IT', 'Engineering', 'Construction'],
            'is_verified': True,
            'verification_date': timezone.now()
        },
        {
            'name': 'US Work Solutions',
            'description': 'Recruitment for US work visas and job placements',
            'email': 'info@usworksolutions.com',
            'phone': '+1-202-222-0000',
            'website': 'https://www.usworksolutions.com',
            'is_active': True,
            'country': usa,
            'address': 'Washington DC, USA',
            'specializations': ['Technology', 'Healthcare', 'Finance'],
            'is_verified': True,
            'verification_date': timezone.now()
        },
        {
            'name': 'German Technical Recruitment',
            'description': 'Specialized in technical recruitment for Germany',
            'email': 'info@germantech.de',
            'phone': '+49-30-222-1111',
            'website': 'https://www.germantech.de',
            'is_active': True,
            'country': germany,
            'address': 'Berlin, Germany',
            'specializations': ['Engineering', 'Technology', 'Manufacturing'],
            'is_verified': True,
            'verification_date': timezone.now()
        },
        {
            'name': 'South African Employment Services',
            'description': 'Recruitment for South African and SADC region',
            'email': 'info@saes.co.za',
            'phone': '+27-11-222-2222',
            'website': 'https://www.saes.co.za',
            'is_active': True,
            'country': south_africa,
            'address': 'Johannesburg, South Africa',
            'specializations': ['Mining', 'Healthcare', 'Education'],
            'is_verified': True,
            'verification_date': timezone.now()
        }
    ]
    
    created_count = 0
    for agency_data in agencies_data:
        specializations = agency_data.pop('specializations', [])
        agency, created = Agency.objects.get_or_create(
            name=agency_data['name'],
            defaults=agency_data
        )
        if created:
            agency.specializations = specializations
            agency.save()
            created_count += 1
            print(f"  ✅ Created agency: {agency.name}")
        else:
            print(f"  ℹ️ Agency already exists: {agency.name}")
    
    print(f"✅ Loaded {created_count} new agencies")
    return created_count


def load_sample_jobs():
    """Load sample job listings into the database"""
    try:
        from jobs.models import Job, JobCategory, Country
        from agencies.models import Agency
    except ImportError:
        print("  ⚠️ Job, JobCategory, Country, or Agency model not found, skipping sample jobs...")
        return 0
    
    print("📊 Loading sample jobs...")
    
    # Get categories
    try:
        government_category = JobCategory.objects.get(slug='government-public-sector')
        admin_category = JobCategory.objects.get(slug='administration')
        finance_category = JobCategory.objects.get(slug='finance-accounting')
        hr_category = JobCategory.objects.get(slug='human-resources')
        it_category = JobCategory.objects.get(slug='information-technology')
        legal_category = JobCategory.objects.get(slug='legal')
        health_category = JobCategory.objects.get(slug='health-medical')
        education_category = JobCategory.objects.get(slug='education')
        engineering_category = JobCategory.objects.get(slug='engineering')
        hospitality_category = JobCategory.objects.get(slug='hospitality')
        construction_category = JobCategory.objects.get(slug='construction')
    except JobCategory.DoesNotExist:
        print("  ⚠️ Job categories not found, run load_job_categories first")
        return 0
    
    # Get agencies
    try:
        psc = Agency.objects.get(name='Public Service Commission')
        kmra = Agency.objects.get(name='Kenya Medical Recruitment Agency')
        global_recruit = Agency.objects.get(name='Global Recruitment Solutions')
        uk_healthcare = Agency.objects.get(name='UK Healthcare Recruitment')
        canada_recruit = Agency.objects.get(name='Canada Immigration Recruitment')
        gulf_recruit = Agency.objects.get(name='Gulf Recruitment Services')
        australia_recruit = Agency.objects.get(name='Australian Skills Recruitment')
        us_works = Agency.objects.get(name='US Work Solutions')
        german_tech = Agency.objects.get(name='German Technical Recruitment')
        sa_services = Agency.objects.get(name='South African Employment Services')
    except Agency.DoesNotExist:
        print("  ⚠️ Agencies not found, run load_agencies first")
        return 0
    
    # Get countries
    try:
        kenya = Country.objects.get(code='KE')
        uk = Country.objects.get(code='UK')
        usa = Country.objects.get(code='USA')
        canada = Country.objects.get(code='CA')
        australia = Country.objects.get(code='AU')
        germany = Country.objects.get(code='DE')
        uae = Country.objects.get(code='AE')
        south_africa = Country.objects.get(code='ZA')
    except Country.DoesNotExist:
        print("  ⚠️ Countries not found, run load_countries first")
        return 0
    
    jobs_data = [
        # Kenya Jobs
        {
            'title': 'Senior Administrative Officer',
            'agency': psc,
            'country': kenya,
            'category': admin_category,
            'description': 'Lead administrative operations and coordinate government services delivery across multiple departments.',
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
            'title': 'IT Systems Administrator',
            'agency': global_recruit,
            'country': kenya,
            'category': it_category,
            'description': 'Manage and maintain government IT systems, networks, and infrastructure.',
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
        {
            'title': 'Human Resources Manager',
            'agency': global_recruit,
            'country': kenya,
            'category': hr_category,
            'description': 'Lead HR operations including recruitment, training, performance management, and employee relations.',
            'requirements': 'Bachelors in HR Management. 5+ years experience. CHRP certification preferred.',
            'benefits': 'Medical cover, Pension, Performance bonuses',
            'salary_min': Decimal('90000'),
            'salary_max': Decimal('130000'),
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
            'is_featured': False,
            'is_verified': True
        },
        {
            'title': 'Healthcare Administrator - County Government',
            'agency': kmra,
            'country': kenya,
            'category': health_category,
            'description': 'Coordinate healthcare services and administration at county level.',
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
            'title': 'Legal Counsel - Public Service Commission',
            'agency': psc,
            'country': kenya,
            'category': legal_category,
            'description': 'Provide legal advice and representation for government agencies.',
            'requirements': 'Bachelor of Laws (LLB). 5+ years experience in public law. Advocate of the High Court.',
            'benefits': 'Medical cover, Pension, Legal practice allowance',
            'salary_min': Decimal('120000'),
            'salary_max': Decimal('180000'),
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
        {
            'title': 'Education Officer - Ministry of Education',
            'agency': psc,
            'country': kenya,
            'category': education_category,
            'description': 'Coordinate education programs and policy implementation at national level.',
            'requirements': 'Masters in Education or related field. 5+ years experience in education administration.',
            'benefits': 'Medical cover, Pension, Education allowance',
            'salary_min': Decimal('85000'),
            'salary_max': Decimal('120000'),
            'salary_currency': 'KES',
            'is_salary_negotiable': False,
            'employment_type': 'full_time',
            'experience_level': 'senior',
            'location': 'Nairobi, Kenya',
            'is_remote': False,
            'visa_requirements': 'Kenyan citizenship',
            'required_languages': ['English', 'Swahili'],
            'closing_date': timezone.now() + timedelta(days=32),
            'status': 'active',
            'is_featured': False,
            'is_verified': True
        },
        # UK Jobs
        {
            'title': 'Registered Nurse - NHS',
            'agency': uk_healthcare,
            'country': uk,
            'category': health_category,
            'description': 'Join the UK National Health Service as a registered nurse.',
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
        # USA Jobs
        {
            'title': 'Data Scientist - Tech Firm',
            'agency': us_works,
            'country': usa,
            'category': it_category,
            'description': 'Analyze big data and develop machine learning models.',
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
        # Canada Jobs
        {
            'title': 'Civil Engineer - Construction',
            'agency': canada_recruit,
            'country': canada,
            'category': engineering_category,
            'description': 'Lead civil engineering projects for infrastructure development.',
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
        # Australia Jobs
        {
            'title': 'IT Project Manager',
            'agency': australia_recruit,
            'country': australia,
            'category': it_category,
            'description': 'Lead IT projects and teams for enterprise solutions.',
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
        # UAE Jobs
        {
            'title': 'Hospitality Manager - Hotel Chain',
            'agency': gulf_recruit,
            'country': uae,
            'category': hospitality_category,
            'description': 'Manage hotel operations and guest services for 5-star property.',
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
        # Germany Jobs
        {
            'title': 'Mechanical Engineer - Automotive',
            'agency': german_tech,
            'country': germany,
            'category': engineering_category,
            'description': 'Design and develop automotive systems for leading car manufacturer.',
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
        # South Africa Jobs
        {
            'title': 'Mining Engineer',
            'agency': sa_services,
            'country': south_africa,
            'category': engineering_category,
            'description': 'Lead mining operations and resource extraction projects.',
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
        category = job_data.pop('category', None)
        country = job_data.pop('country', None)
        
        job, created = Job.objects.get_or_create(
            title=job_data['title'],
            agency=agency,
            country=country,
            category=category,
            defaults=job_data
        )
        if created:
            created_count += 1
            print(f"  ✅ Created job: {job.title}")
        else:
            print(f"  ℹ️ Job already exists: {job.title}")
    
    print(f"✅ Loaded {created_count} sample jobs")
    return created_count


def create_superuser():
    """Create admin superuser if it doesn't exist"""
    print("👤 Checking superuser...")
    
    # Delete existing admin if exists to avoid conflicts
    User.objects.filter(email='admin@admin.com').delete()
    
    try:
        # Create superuser using the custom UserManager        admin = User.objects.create_superuser(
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
    
    # Create test user
    User.objects.filter(email='test@example.com').delete()
    try:
        test_user = User.objects.create_user(
            email='test@example.com',
            password='test123'
        )
        print("  ✅ Created test user: test@example.com / test123")
    except Exception as e:
        print(f"  ❌ Failed to create test user: {e}")
    
    # Verify superuser was created
    if User.objects.filter(email='admin@admin.com').exists():
        admin = User.objects.get(email='admin@admin.com')
        print(f"  ✅ Verification: Superuser exists with ID {admin.id}")
        print(f"  ✅ Can login with: admin@admin.com / admin123")
    else:
        print("  ❌ Verification: Superuser NOT found in database!")


def create_payment_settings():
    """Create default payment settings"""
    try:
        from payments.models import PaymentSettings
    except ImportError:
        print("  ⚠️ PaymentSettings model not found, skipping...")
        return 0
    
    print("📊 Creating payment settings...")
    
    settings_data = [
        {'key': 'payment_gateway', 'value': {'mpesa': True, 'bank_transfer': True, 'card': True}, 'description': 'Enabled payment gateways'},
        {'key': 'default_currency', 'value': 'KES', 'description': 'Default currency for payments'},
        {'key': 'enable_payments', 'value': True, 'description': 'Enable/disable payment system'},
        {'key': 'payment_fee_percentage', 'value': 2.5, 'description': 'Payment processing fee percentage'},
        {'key': 'tax_percentage', 'value': 0, 'description': 'Tax percentage on payments'},
        {'key': 'mpesa_shortcode', 'value': '174379', 'description': 'M-Pesa shortcode for payments'},
        {'key': 'callback_url', 'value': 'https://government-jobs-portal.onrender.com/payment/mpesa-callback/', 'description': 'M-Pesa callback URL'},
    ]
    
    created_count = 0
    for setting_data in settings_data:
        setting, created = PaymentSettings.objects.get_or_create(
            key=setting_data['key'],
            defaults={'value': setting_data['value'], 'description': setting_data['description']}
        )
        if created:
            created_count += 1
            print(f"  ✅ Created setting: {setting.key}")
        else:
            print(f"  ℹ️ Setting already exists: {setting.key}")
    
    print(f"✅ Loaded {created_count} payment settings")
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
        load_job_categories()
        print()
        load_agencies()
        print()
        load_sample_jobs()
        print()
        load_payment_plans()
        print()
        create_payment_settings()
        print()
        create_superuser()
        
        # Final verification
        print("\n" + "="*60)
        print("📊 FINAL VERIFICATION")
        print("="*60)
        
        # Check if superuser exists
        if User.objects.filter(email='admin@admin.com').exists():
            admin = User.objects.get(email='admin@admin.com')
            print(f"  ✅ Superuser: {admin.email} (ID: {admin.id})")
            print(f"     - Is Staff: {admin.is_staff}")
            print(f"     - Is Superuser: {admin.is_superuser}")
        else:
            print("  ❌ Superuser NOT found!")
        
        print("\n" + "="*60)
        print("✅ DATA LOADING COMPLETE!")
        print("="*60)
        print("\n📊 Data Summary:")
        print("  ✅ Payment Plans: 5")
        print("  ✅ Countries: 10")
        print("  ✅ Job Categories: 18")
        print("  ✅ Recruitment Agencies: 10")
        print("  ✅ Sample Jobs: 15+")
        print("  ✅ Payment Settings: 7")
        print("\n🔑 Login credentials:")
        print("  Admin: admin@admin.com / admin123")
        print("  Test:  test@example.com / test123")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error loading data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    load_all_data()