from django.db import migrations
import uuid

def create_countries(apps, schema_editor):
    Country = apps.get_model('jobs', 'Country')
    
    countries = [
        {'name': 'Afghanistan', 'code': 'AF', 'currency': 'AFN', 'currency_symbol': '؋'},
        {'name': 'Albania', 'code': 'AL', 'currency': 'ALL', 'currency_symbol': 'L'},
        {'name': 'Algeria', 'code': 'DZ', 'currency': 'DZD', 'currency_symbol': 'دج'},
        {'name': 'Argentina', 'code': 'AR', 'currency': 'ARS', 'currency_symbol': '$'},
        {'name': 'Australia', 'code': 'AU', 'currency': 'AUD', 'currency_symbol': '$'},
        {'name': 'Austria', 'code': 'AT', 'currency': 'EUR', 'currency_symbol': '€'},
        {'name': 'Bangladesh', 'code': 'BD', 'currency': 'BDT', 'currency_symbol': '৳'},
        {'name': 'Belgium', 'code': 'BE', 'currency': 'EUR', 'currency_symbol': '€'},
        {'name': 'Botswana', 'code': 'BW', 'currency': 'BWP', 'currency_symbol': 'P'},
        {'name': 'Brazil', 'code': 'BR', 'currency': 'BRL', 'currency_symbol': 'R$'},
        {'name': 'Canada', 'code': 'CA', 'currency': 'CAD', 'currency_symbol': '$'},
        {'name': 'China', 'code': 'CN', 'currency': 'CNY', 'currency_symbol': '¥'},
        {'name': 'Denmark', 'code': 'DK', 'currency': 'DKK', 'currency_symbol': 'kr'},
        {'name': 'Egypt', 'code': 'EG', 'currency': 'EGP', 'currency_symbol': 'E£'},
        {'name': 'Ethiopia', 'code': 'ET', 'currency': 'ETB', 'currency_symbol': 'Br'},
        {'name': 'Finland', 'code': 'FI', 'currency': 'EUR', 'currency_symbol': '€'},
        {'name': 'France', 'code': 'FR', 'currency': 'EUR', 'currency_symbol': '€'},
        {'name': 'Germany', 'code': 'DE', 'currency': 'EUR', 'currency_symbol': '€'},
        {'name': 'Ghana', 'code': 'GH', 'currency': 'GHS', 'currency_symbol': 'GH₵'},
        {'name': 'India', 'code': 'IN', 'currency': 'INR', 'currency_symbol': '₹'},
        {'name': 'Indonesia', 'code': 'ID', 'currency': 'IDR', 'currency_symbol': 'Rp'},
        {'name': 'Italy', 'code': 'IT', 'currency': 'EUR', 'currency_symbol': '€'},
        {'name': 'Jamaica', 'code': 'JM', 'currency': 'JMD', 'currency_symbol': 'J$'},
        {'name': 'Japan', 'code': 'JP', 'currency': 'JPY', 'currency_symbol': '¥'},
        {'name': 'Kenya', 'code': 'KE', 'currency': 'KES', 'currency_symbol': 'KSh'},
        {'name': 'Malaysia', 'code': 'MY', 'currency': 'MYR', 'currency_symbol': 'RM'},
        {'name': 'Mexico', 'code': 'MX', 'currency': 'MXN', 'currency_symbol': '$'},
        {'name': 'Namibia', 'code': 'NA', 'currency': 'NAD', 'currency_symbol': '$'},
        {'name': 'Netherlands', 'code': 'NL', 'currency': 'EUR', 'currency_symbol': '€'},
        {'name': 'New Zealand', 'code': 'NZ', 'currency': 'NZD', 'currency_symbol': '$'},
        {'name': 'Nigeria', 'code': 'NG', 'currency': 'NGN', 'currency_symbol': '₦'},
        {'name': 'Norway', 'code': 'NO', 'currency': 'NOK', 'currency_symbol': 'kr'},
        {'name': 'Pakistan', 'code': 'PK', 'currency': 'PKR', 'currency_symbol': '₨'},
        {'name': 'Philippines', 'code': 'PH', 'currency': 'PHP', 'currency_symbol': '₱'},
        {'name': 'Poland', 'code': 'PL', 'currency': 'PLN', 'currency_symbol': 'zł'},
        {'name': 'Portugal', 'code': 'PT', 'currency': 'EUR', 'currency_symbol': '€'},
        {'name': 'Russia', 'code': 'RU', 'currency': 'RUB', 'currency_symbol': '₽'},
        {'name': 'Rwanda', 'code': 'RW', 'currency': 'RWF', 'currency_symbol': 'FRw'},
        {'name': 'Saudi Arabia', 'code': 'SA', 'currency': 'SAR', 'currency_symbol': '﷼'},
        {'name': 'Singapore', 'code': 'SG', 'currency': 'SGD', 'currency_symbol': '$'},
        {'name': 'South Africa', 'code': 'ZA', 'currency': 'ZAR', 'currency_symbol': 'R'},
        {'name': 'South Korea', 'code': 'KR', 'currency': 'KRW', 'currency_symbol': '₩'},
        {'name': 'Spain', 'code': 'ES', 'currency': 'EUR', 'currency_symbol': '€'},
        {'name': 'Sweden', 'code': 'SE', 'currency': 'SEK', 'currency_symbol': 'kr'},
        {'name': 'Switzerland', 'code': 'CH', 'currency': 'CHF', 'currency_symbol': 'CHF'},
        {'name': 'Tanzania', 'code': 'TZ', 'currency': 'TZS', 'currency_symbol': 'TSh'},
        {'name': 'Thailand', 'code': 'TH', 'currency': 'THB', 'currency_symbol': '฿'},
        {'name': 'Turkey', 'code': 'TR', 'currency': 'TRY', 'currency_symbol': '₺'},
        {'name': 'Uganda', 'code': 'UG', 'currency': 'UGX', 'currency_symbol': 'USh'},
        {'name': 'United Arab Emirates', 'code': 'AE', 'currency': 'AED', 'currency_symbol': 'د.إ'},
        {'name': 'United Kingdom', 'code': 'GB', 'currency': 'GBP', 'currency_symbol': '£'},
        {'name': 'United States', 'code': 'US', 'currency': 'USD', 'currency_symbol': '$'},
        {'name': 'Vietnam', 'code': 'VN', 'currency': 'VND', 'currency_symbol': '₫'},
        {'name': 'Zambia', 'code': 'ZM', 'currency': 'ZMW', 'currency_symbol': 'ZK'},
        {'name': 'Zimbabwe', 'code': 'ZW', 'currency': 'ZWL', 'currency_symbol': '$'},
    ]
    
    for country_data in countries:
        Country.objects.create(
            id=uuid.uuid4(),
            name=country_data['name'],
            code=country_data['code'],
            currency=country_data['currency'],
            currency_symbol=country_data['currency_symbol'],
            is_active=True
        )

def create_categories(apps, schema_editor):
    Category = apps.get_model('jobs', 'Category')
    
    categories = [
        {'name': 'Accounting & Finance', 'icon': 'fa-calculator'},
        {'name': 'Administration & Office Support', 'icon': 'fa-briefcase'},
        {'name': 'Agriculture & Farming', 'icon': 'fa-seedling'},
        {'name': 'Architecture & Design', 'icon': 'fa-pencil-ruler'},
        {'name': 'Art & Creative', 'icon': 'fa-palette'},
        {'name': 'Automotive', 'icon': 'fa-car'},
        {'name': 'Banking & Financial Services', 'icon': 'fa-university'},
        {'name': 'Construction & Building', 'icon': 'fa-hard-hat'},
        {'name': 'Consulting & Strategy', 'icon': 'fa-chart-line'},
        {'name': 'Customer Service & Support', 'icon': 'fa-headset'},
        {'name': 'Education & Training', 'icon': 'fa-graduation-cap'},
        {'name': 'Engineering & Technology', 'icon': 'fa-microchip'},
        {'name': 'Healthcare & Medical', 'icon': 'fa-heartbeat'},
        {'name': 'Hospitality & Tourism', 'icon': 'fa-hotel'},
        {'name': 'Human Resources', 'icon': 'fa-users'},
        {'name': 'Information Technology', 'icon': 'fa-laptop-code'},
        {'name': 'Legal & Compliance', 'icon': 'fa-gavel'},
        {'name': 'Logistics & Supply Chain', 'icon': 'fa-truck'},
        {'name': 'Manufacturing & Production', 'icon': 'fa-industry'},
        {'name': 'Marketing & Communications', 'icon': 'fa-bullhorn'},
        {'name': 'Media & Journalism', 'icon': 'fa-newspaper'},
        {'name': 'Non-Profit & NGO', 'icon': 'fa-hand-holding-heart'},
        {'name': 'Project Management', 'icon': 'fa-tasks'},
        {'name': 'Real Estate & Property', 'icon': 'fa-home'},
        {'name': 'Retail & Sales', 'icon': 'fa-store'},
        {'name': 'Science & Research', 'icon': 'fa-flask'},
        {'name': 'Sports & Recreation', 'icon': 'fa-running'},
        {'name': 'Transportation & Logistics', 'icon': 'fa-shipping-fast'},
        {'name': 'Travel & Tourism', 'icon': 'fa-plane'},
        {'name': 'Warehouse & Distribution', 'icon': 'fa-warehouse'},
    ]
    
    for category_data in categories:
        Category.objects.create(
            id=uuid.uuid4(),
            name=category_data['name'],
            icon=category_data['icon'],
            is_active=True
        )

class Migration(migrations.Migration):
    dependencies = [
        ('jobs', '0001_initial'),  # Replace with your actual migration
    ]
    
    operations = [
        migrations.RunPython(create_countries),
        migrations.RunPython(create_categories),
    ]