"""
Sitemap configuration for Government Jobs Portal
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from jobs.models import Job
from employers.models import EmployerProfile
from agencies.models import RecruitmentAgency


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'about', 'contact', 'faq', 'privacy_policy', 'terms', 'help']

    def location(self, item):
        return reverse(item)


class JobSitemap(Sitemap):
    """Sitemap for job listings"""
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return Job.objects.filter(status='active')

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at


class EmployerSitemap(Sitemap):
    """Sitemap for employers"""
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return EmployerProfile.objects.filter(is_verified=True)

    def lastmod(self, obj):
        return obj.updated_at


class AgencySitemap(Sitemap):
    """Sitemap for recruitment agencies"""
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return RecruitmentAgency.objects.filter(is_verified=True)

    def lastmod(self, obj):
        return obj.updated_at
