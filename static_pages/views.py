"""
Static Pages Views
Handles static pages like Home, About, Contact, FAQ, etc.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.utils import timezone

from jobs.models import Job, Category, Country, JobApplication
from accounts.models import User
from employers.models import EmployerProfile
from agencies.models import RecruitmentAgency
from payments.models import Payment


def home(request):
    """Home/Landing Page"""
    
    # Get statistics
    stats = {
        'available_jobs': Job.objects.filter(status='active', closing_date__gte=timezone.now()).count(),
        'registered_job_seekers': User.objects.filter(user_type='citizen', status='approved').count(),
        'verified_employers': EmployerProfile.objects.filter(is_verified=True).count(),
        'countries_recruiting': Job.objects.filter(status='active').values('country').distinct().count(),
        'successful_placements': JobApplication.objects.filter(status='accepted').count(),
        'licensed_recruitment_agencies': RecruitmentAgency.objects.filter(is_verified=True).count(),
    }
    
    # Get featured jobs (limit to 10)
    featured_jobs = Job.objects.filter(
        status='active',
        is_featured=True,
        is_verified=True,
        closing_date__gte=timezone.now()
    ).select_related('country', 'category', 'employer', 'agency').order_by('-posted_date')[:10]
    
    # Get top countries with job counts
    from django.db.models import Count
    top_countries = Country.objects.filter(
        jobs__status='active',
        jobs__closing_date__gte=timezone.now()
    ).annotate(
        job_count=Count('jobs')
    ).filter(job_count__gt=0).order_by('-job_count')[:12]
    
    # Get categories with job counts
    categories = Category.objects.filter(
        jobs__status='active',
        jobs__closing_date__gte=timezone.now()
    ).annotate(
        job_count=Count('jobs')
    ).filter(job_count__gt=0).order_by('name')
    
    # Success stories (sample data - you can replace with model data)
    success_stories = [
        {
            'name': 'James Mwangi',
            'position': 'Software Developer',
            'testimonial': 'The Government Jobs Portal helped me find a verified job in Canada. The process was transparent and secure.',
            'country': 'Canada'
        },
        {
            'name': 'Sarah Akinyi',
            'position': 'Registered Nurse',
            'testimonial': 'I got placed in the UK through a licensed recruitment agency on this platform. Highly recommended!',
            'country': 'United Kingdom'
        },
        {
            'name': 'David Ochieng',
            'position': 'Civil Engineer',
            'testimonial': 'This platform saved me from recruitment fraud. The government verification gave me peace of mind.',
            'country': 'Germany'
        },
    ]
    
    # Announcements (sample data - you can replace with model data)
    announcements = [
        {
            'category': 'Recruitment Drive',
            'title': 'Mass Recruitment for Healthcare Workers',
            'summary': 'The Ministry of Labour announces a major recruitment drive for healthcare workers to the UK.',
            'date': timezone.now() - timezone.timedelta(days=2)
        },
        {
            'category': 'Program',
            'title': 'Youth Employment Program 2026',
            'summary': 'Apply for the government-sponsored youth employment program with opportunities in ICT and Engineering.',
            'date': timezone.now() - timezone.timedelta(days=5)
        },
        {
            'category': 'Announcement',
            'title': 'New Labour Agreement with Germany',
            'summary': 'Kenya and Germany sign new labour agreement for skilled workers in engineering and technology.',
            'date': timezone.now() - timezone.timedelta(days=10)
        },
    ]
    
    # FAQs (sample data - you can replace with model data)
    faqs = [
        {
            'question': 'How do I register on the portal?',
            'answer': 'Click on the Register button and fill in your personal information, then upload the required documents for verification.'
        },
        {
            'question': 'What is the government employment service fee?',
            'answer': 'This is a nominal fee required to access job applications on the portal. It helps maintain the platform and ensure quality services.'
        },
        {
            'question': 'How do I know if a job is verified?',
            'answer': 'All jobs on the portal are verified by the government. Look for the "Verified" badge on job listings.'
        },
        {
            'question': 'Can I apply for jobs in multiple countries?',
            'answer': 'Yes, you can apply for jobs in any country listed on the portal, provided you meet the requirements.'
        },
        {
            'question': 'What documents do I need to upload?',
            'answer': 'You need to upload your CV, National ID, Passport, Academic Certificates, Professional Certificates, and a passport-size photo.'
        },
        {
            'question': 'How long does the verification process take?',
            'answer': 'Verification typically takes 2-3 business days. You will be notified via email once your account is verified.'
        },
    ]
    
    context = {
        'stats': stats,
        'featured_jobs': featured_jobs,
        'top_countries': top_countries,
        'categories': categories,
        'success_stories': success_stories,
        'announcements': announcements,
        'faqs': faqs,
    }
    
    return render(request, 'home.html', context)


def about(request):
    """About Us Page"""
    return render(request, 'static_pages/about.html')


def contact(request):
    """Contact Page"""
    return render(request, 'static_pages/contact.html')


def faq(request):
    """FAQ Page"""
    faqs = [
        {
            'question': 'How do I register on the portal?',
            'answer': 'Click on the Register button and fill in your personal information, then upload the required documents for verification.'
        },
        {
            'question': 'What is the government employment service fee?',
            'answer': 'This is a nominal fee required to access job applications on the portal. It helps maintain the platform and ensure quality services.'
        },
        {
            'question': 'How do I know if a job is verified?',
            'answer': 'All jobs on the portal are verified by the government. Look for the "Verified" badge on job listings.'
        },
        {
            'question': 'Can I apply for jobs in multiple countries?',
            'answer': 'Yes, you can apply for jobs in any country listed on the portal, provided you meet the requirements.'
        },
        {
            'question': 'What documents do I need to upload?',
            'answer': 'You need to upload your CV, National ID, Passport, Academic Certificates, Professional Certificates, and a passport-size photo.'
        },
        {
            'question': 'How long does the verification process take?',
            'answer': 'Verification typically takes 2-3 business days. You will be notified via email once your account is verified.'
        },
        {
            'question': 'What payment methods are accepted?',
            'answer': 'We accept M-Pesa, eCitizen, Bank Transfer, Visa, and Mastercard.'
        },
        {
            'question': 'How can I track my application status?',
            'answer': 'You can track your application status through your dashboard. You will also receive email and SMS notifications.'
        },
    ]
    return render(request, 'static_pages/faq.html', {'faqs': faqs})


def privacy_policy(request):
    """Privacy Policy Page"""
    return render(request, 'static_pages/privacy_policy.html')


def terms_conditions(request):
    """Terms and Conditions Page"""
    return render(request, 'static_pages/terms.html')


def help_center(request):
    """Help Center Page"""
    return render(request, 'static_pages/help.html')


def sitemap(request):
    """Sitemap Page"""
    return render(request, 'static_pages/sitemap.html')


@require_POST
def contact_submit(request):
    """Handle contact form submission"""
    name = request.POST.get('name')
    email = request.POST.get('email')
    subject = request.POST.get('subject')
    message = request.POST.get('message')
    
    if not all([name, email, subject, message]):
        messages.error(request, 'All fields are required.')
        return redirect('contact')
    
    try:
        # Send email
        full_message = f"Name: {name}\nEmail: {email}\n\n{message}"
        send_mail(
            subject=f"Contact Form: {subject}",
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        messages.success(request, 'Your message has been sent successfully. We will get back to you soon.')
    except Exception as e:
        messages.error(request, 'There was an error sending your message. Please try again later.')
    
    return redirect('contact')


@require_POST
def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    email = request.POST.get('email')
    
    if not email:
        messages.error(request, 'Please enter your email address.')
        return redirect('home')
    
    # You can save to database here if you have a newsletter model
    messages.success(request, 'Thank you for subscribing to our newsletter!')
    return redirect('home')


def newsletter_unsubscribe(request, token):
    """Handle newsletter unsubscribe"""
    # Implement unsubscribe logic here
    messages.success(request, 'You have been unsubscribed from our newsletter.')
    return redirect('home')