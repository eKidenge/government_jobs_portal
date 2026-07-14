"""
Static Pages App URLs
"""
from django.urls import path
from . import views

# app_name = 'static_pages'  # COMMENT THIS OUT or remove it

urlpatterns = [
    # Home Page
    path('', views.home, name='home'),
    
    # Information Pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    
    # Legal Pages
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms'),
    path('help/', views.help_center, name='help'),
    
    # Sitemap
    path('sitemap/', views.sitemap, name='sitemap'),
    
    # Contact Form Submission
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/unsubscribe/<str:token>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
]