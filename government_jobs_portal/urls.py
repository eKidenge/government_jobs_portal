"""
URL configuration for government_jobs_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Import static_pages views for home
from static_pages import views as static_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home/Landing Page - using static_pages app
    path('', static_views.home, name='home'),
    
    # ==============================================
    # APP URLS - Each app handles its own URLs
    # ==============================================
    
    # Accounts App (Authentication & User Management)
    path('', include('accounts.urls')),
    
    # Jobs App
    path('', include('jobs.urls')),
    
    # Payments App
    path('', include('payments.urls')),
    
    # Employers App
    path('', include('employers.urls')),
    
    # Agencies App (Recruitment Agencies)
    path('', include('agencies.urls')),
    
    # Notifications App
    path('', include('notifications.urls')),
    
    # Static Pages App (About, Contact, FAQ, etc.)
    path('', include('static_pages.urls')),
    
    # ==============================================
    # API ENDPOINTS
    # ==============================================
    
    # JWT Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API endpoints for each app
    path('api/accounts/', include('accounts.api_urls')),
    path('api/jobs/', include('jobs.api_urls')),
    path('api/payments/', include('payments.api_urls')),
    path('api/employers/', include('employers.api_urls')),
    path('api/agencies/', include('agencies.api_urls')),
    path('api/notifications/', include('notifications.api_urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar (optional)
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]