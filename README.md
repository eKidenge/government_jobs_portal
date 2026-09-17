# Government Jobs Portal

A comprehensive Django-based platform connecting citizens to verified employment opportunities worldwide through a transparent, government-managed recruitment system.

## Overview

The Government Jobs Portal is a secure, centralized digital platform that enables citizens to access verified job opportunities while eliminating recruitment fraud. It provides government oversight, employer verification, secure payment processing, and comprehensive application management.

## 1. Overview Diagram
```mermaid
flowchart TD
    START([User Visits Portal]) --> LAND[Public Landing Page]
    LAND --> CHOICE{Has Account?}

    CHOICE -- No --> REG[Multi-Step Registration]
    CHOICE -- Yes --> LOGIN[Login]

    REG --> DOCS[Document Upload]
    DOCS --> VERIFY[Admin Verification]
    VERIFY --> LOGIN
    LOGIN --> ROLE{Role?}

    ROLE -- Citizen --> CITIZEN[Citizen Dashboard]
    ROLE -- Employer --> EMPLOYER[Employer Dashboard]
    ROLE -- Agency --> AGENCY[Agency Dashboard]
    ROLE -- Administrator --> ADMIN[Admin Dashboard]

    CITIZEN --> BROWSE[Browse & Apply Jobs]
    EMPLOYER --> POST[Post & Manage Jobs]
    AGENCY --> OVERSEAS[Post Overseas Jobs]
    ADMIN --> CONTROL[Verify, Approve, Report]

    BROWSE --> PAYMENT[Secure Payment]
    PAYMENT --> TRACK[Application Tracking]

    classDef entry fill:#4A90E2,stroke:#1F3A5F,color:#fff
    classDef auth fill:#7ED321,stroke:#3B6B00,color:#fff
    classDef role fill:#9013FE,stroke:#4A0A85,color:#fff
    classDef admin fill:#D0021B,stroke:#6B000D,color:#fff
    classDef pay fill:#F5A623,stroke:#8B5A00,color:#fff
    class START,LAND,CHOICE entry
    class REG,LOGIN,DOCS,VERIFY auth
    class CITIZEN,EMPLOYER,AGENCY,ROLE,BROWSE,POST,OVERSEAS,TRACK role
    class ADMIN,CONTROL admin
    class PAYMENT pay
```
## 2. Registration, Verification & Login Flow
```mermaid
flowchart TD
    A([Start]) --> B{Has Account?}

    B -- No --> C[Select Account Type]
    C --> C1[Citizen]
    C --> C2[Employer]
    C --> C3[Agency]

    C1 --> D[Multi-Step Registration]
    C2 --> D
    C3 --> D
    D --> E[Fill Details]
    E --> F[Upload Documents]
    F --> G{Valid Input?}
    G -- No --> H[Show Errors] --> E
    G -- Yes --> I[Submit for Verification]

    I --> J{Admin Approval?}
    J -- Rejected --> K[Notify & Request Resubmission] --> E
    J -- Approved --> L[Account Activated]

    B -- Yes --> M[Login Page]
    L --> M
    M --> N[Enter Credentials]
    N --> O{Valid?}
    O -- No --> P[Invalid Credentials] --> M
    O -- Yes --> Q{Account Active?}
    Q -- No --> R[Suspended / Pending - Contact Admin]
    Q -- Yes --> S{Role?}

    S -- Citizen --> T1[Citizen Dashboard]
    S -- Employer --> T2[Employer Dashboard]
    S -- Agency --> T3[Agency Dashboard]
    S -- Administrator --> T4[Admin Dashboard]

    classDef reg fill:#F5A623,stroke:#8B5A00,color:#fff
    classDef auth fill:#7ED321,stroke:#3B6B00,color:#fff
    classDef role fill:#9013FE,stroke:#4A0A85,color:#fff
    class C,C1,C2,C3,D,E,F,G,H,I,J,K reg
    class M,N,O,P,Q,R auth
    class S,T1,T2,T3,T4 role
```
## Features

### For Citizens
- Browse verified job opportunities
- Multi-step registration with document upload
- Secure payment processing (M-Pesa, eCitizen, Bank Transfer, Visa, Mastercard)
- Personal dashboard with application tracking
- Real-time notifications
- Application status tracking (Submitted → Under Review → Shortlisted → Interview → Accepted)
  ## 3. Citizen Flow
```mermaid
flowchart TD
    A[Citizen Dashboard] --> B[Browse Jobs]
    A --> C[My Applications]
    A --> D[Payments]
    A --> E[Notifications]
    A --> F[Profile & Documents]

    B --> B1[Search & Filter]
    B1 --> B2[View Job Details]
    B2 --> B3{Apply?}
    B3 -- No --> B1
    B3 -- Yes --> B4[Submit Application]

    B4 --> C1[Payment Required?]
    C1 -- Yes --> G[Secure Payment]
    C1 -- No --> H[Application Submitted]

    G --> G1{M-Pesa / eCitizen / Bank / Visa / Mastercard}
    G1 --> G2[Payment Verification]
    G2 --> H

    H --> C
    C --> C2{Status}
    C2 -- Submitted --> C3[Awaiting Review]
    C2 -- Under Review --> C4[Being Reviewed]
    C2 -- Shortlisted --> C5[Shortlisted]
    C2 -- Interview --> C6[Interview Scheduled]
    C2 -- Accepted --> C7[Offer Accepted]
    C2 -- Rejected --> C8[Not Successful]

    E --> E1[Real-Time Alerts]
    E --> E2[Status Updates]

    classDef citizen fill:#50E3C2,stroke:#1F7A66,color:#000
    classDef pay fill:#F5A623,stroke:#8B5A00,color:#fff
    class A,B,C,D,E,F,B1,B2,B3,B4,C1,C2,C3,C4,C5,C6,C7,C8,E1,E2 citizen
    class G,G1,G2,H pay
```

### For Employers
- Company registration and verification
- Job posting and management
- Application review and management
- CV downloads
- Candidate shortlisting and interview scheduling
## 4. Employer Flow
```mermaid
flowchart TD
    A[Employer Dashboard] --> B[Company Profile]
    A --> C[Post Job]
    A --> D[Manage Jobs]
    A --> E[Applications]
    A --> F[Shortlisting & Interviews]

    B --> B1[Company Registration]
    B --> B2[Verification Status]
    B --> B3[Upload Documents]

    C --> C1[Job Details]
    C1 --> C2[Submit for Approval]
    C2 --> C3{Admin Approved?}
    C3 -- No --> C4[Revise & Resubmit]
    C3 -- Yes --> C5[Job Live]

    D --> D1[Edit Job]
    D --> D2[Close Job]
    D --> D3[Feature Job]

    E --> E1[View Applicants]
    E --> E2[Download CVs]
    E --> E3[Filter & Sort]

    F --> F1[Shortlist Candidate]
    F --> F2[Schedule Interview]
    F --> F3[Send Offer]
    F --> F4[Reject Applicant]

    classDef emp fill:#4A90E2,stroke:#1F3A5F,color:#fff
    class A,B,C,D,E,F,B1,B2,B3,C1,C2,C3,C4,C5,D1,D2,D3,E1,E2,E3,F1,F2,F3,F4 emp
```

### For Recruitment Agencies
- Agency registration and accreditation
- Overseas job posting
- Applicant management
- Contract uploads
- Recruitment progress tracking
  ## 5. Recruitment Agency Flow
  ```mermaid
flowchart TD
    A[Agency Dashboard] --> B[Agency Profile]
    A --> C[Post Overseas Jobs]
    A --> D[Manage Jobs]
    A --> E[Applicant Management]
    A --> F[Contract Uploads]
    A --> G[Recruitment Progress]

    B --> B1[Agency Registration]
    B --> B2[Accreditation Status]
    B --> B3[Upload Licenses]

    C --> C1[Job Details + Country]
    C1 --> C2[Submit for Approval]
    C2 --> C3{Admin Approved?}
    C3 -- No --> C4[Revise & Resubmit]
    C3 -- Yes --> C5[Job Live]

    E --> E1[View Applicants]
    E --> E2[Shortlist]
    E --> E3[Schedule Interviews]
    E --> E4[Track Progress]

    F --> F1[Upload Contract]
    F --> F2[Attach to Candidate]

    G --> G1[Application Stages]
    G --> G2[Deployment Status]

    classDef agency fill:#9013FE,stroke:#4A0A85,color:#fff
    class A,B,C,D,E,F,G,B1,B2,B3,C1,C2,C3,C4,C5,E1,E2,E3,E4,F1,F2,G1,G2 agency
```

### For Administrators
- Comprehensive dashboard with analytics
- User management (approve, suspend, activate)
- Job management (approve, reject, feature)
- Employer and agency verification
- Payment verification and refunds
- Reports generation (CSV, Excel, PDF)
## 6. Administrator Flow
```mermaid
flowchart TD
    A[Admin Dashboard] --> B[Analytics Overview]
    A --> C[User Management]
    A --> D[Job Management]
    A --> E[Employer Verification]
    A --> F[Agency Verification]
    A --> G[Payment Verification]
    A --> H[Reports]

    C --> C1[Approve User]
    C --> C2[Suspend User]
    C --> C3[Activate User]
    C --> C4[Delete User]

    D --> D1[Approve Job]
    D --> D2[Reject Job]
    D --> D3[Feature Job]

    E --> E1[Review Company Docs]
    E --> E2[Approve / Reject Employer]

    F --> F1[Review Agency Docs]
    F --> F2[Approve / Reject Agency]
    F --> F3[Grant Accreditation]

    G --> G1[Verify Payments]
    G --> G2[Process Refunds]

    H --> H1[CSV Export]
    H --> H2[Excel Export]
    H --> H3[PDF Export]

    classDef admin fill:#D0021B,stroke:#6B000D,color:#fff
    class A,B,C,D,E,F,G,H,C1,C2,C3,C4,D1,D2,D3,E1,E2,F1,F2,F3,G1,G2,H1,H2,H3 admin
```
## 7. Application Lifecycle (Sequence)
```mermaid
sequenceDiagram
    participant C as Citizen
    participant P as Payment Gateway
    participant E as Employer / Agency
    participant A as Admin
    participant N as Notification

    C->>C: Browse & Select Job
    C->>C: Submit Application
    C->>P: Pay Application Fee
    P->>A: Verify Payment
    A->>C: Confirm Payment
    C->>E: Application Delivered
    E->>E: Review Application
    E->>C: Status: Under Review
    E->>C: Status: Shortlisted
    E->>C: Schedule Interview
    E->>C: Status: Interview
    E->>C: Send Offer
    C->>E: Accept Offer
    E->>A: Report Hire
    A->>N: Log Completion
    N->>C: Final Notification
```
## 8. Payment Flow
```mermaid
flowchart TD
    A[Application Submitted] --> B{Payment Required?}
    B -- No --> C[Application Complete]
    B -- Yes --> D[Select Payment Method]

    D --> E1[M-Pesa]
    D --> E2[eCitizen]
    D --> E3[Bank Transfer]
    D --> E4[Visa]
    D --> E5[Mastercard]

    E1 --> F[Payment Gateway]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F

    F --> G{Payment Success?}
    G -- No --> H[Retry / Cancel]
    H --> D
    G -- Yes --> I[Generate Receipt]
    I --> J[Admin Verification]
    J --> K{Verified?}
    K -- No --> L[Flag for Review]
    K -- Yes --> C
    L --> M[Refund Processed]

    classDef pay fill:#F5A623,stroke:#8B5A00,color:#fff
    classDef admin fill:#D0021B,stroke:#6B000D,color:#fff
    class A,B,C,D,E1,E2,E3,E4,E5,F,G,H,I pay
    class J,K,L,M admin
```
## 9. Job Posting & Approval Flow
```mermaid
flowchart TD
    A[Employer / Agency] --> B[Create Job Post]
    B --> C[Fill Job Details]
    C --> D[Submit for Approval]
    D --> E[Admin Review]

    E --> F{Decision}
    F -- Approve --> G[Job Published]
    F -- Reject --> H[Notify Employer]
    F -- Feature --> I[Featured Listing]

    H --> J[Revise & Resubmit] --> D

    G --> K[Visible to Citizens]
    I --> K
    K --> L[Applications Received]

    classDef emp fill:#4A90E2,stroke:#1F3A5F,color:#fff
    classDef admin fill:#D0021B,stroke:#6B000D,color:#fff
    classDef live fill:#7ED321,stroke:#3B6B00,color:#fff
    class A,B,C,D,H,J emp
    class E,F admin
    class G,I,K,L live
```
## 10. Notification Flow
```mermaid
flowchart LR
    EV[Event Triggered] --> R{Role}
    R -- Citizen --> C1[Application Status Update]
    R -- Citizen --> C2[Payment Confirmation]
    R -- Citizen --> C3[Interview Invitation]
    R -- Employer --> E1[New Application]
    R -- Employer --> E2[Job Approved]
    R -- Agency --> A1[Applicant Update]
    R -- Admin --> AD1[Verification Pending]
    R -- Admin --> AD2[Payment Flagged]

    C1 --> N[Notification Service]
    C2 --> N
    C3 --> N
    E1 --> N
    E2 --> N
    A1 --> N
    AD1 --> N
    AD2 --> N

    N --> D1[Email]
    N --> D2[SMS]
    N --> D3[In-App Alert]

    classDef citizen fill:#50E3C2,stroke:#1F7A66,color:#000
    classDef emp fill:#4A90E2,stroke:#1F3A5F,color:#fff
    classDef agency fill:#9013FE,stroke:#4A0A85,color:#fff
    classDef admin fill:#D0021B,stroke:#6B000D,color:#fff
    classDef notif fill:#F5A623,stroke:#8B5A00,color:#fff
    class C1,C2,C3 citizen
    class E1,E2 emp
    class A1 agency
    class AD1,AD2 admin
    class N,D1,D2,D3 notif
```
## 11. Reports & Analytics
```mermaid
flowchart TD
    A[Admin Reports] --> B{Report Type}
    B --> C[User Reports]
    B --> D[Job Reports]
    B --> E[Application Reports]
    B --> F[Payment Reports]
    B --> G[Verification Reports]

    C --> H[Export Format]
    D --> H
    E --> H
    F --> H
    G --> H

    H --> H1[CSV]
    H --> H2[Excel]
    H --> H3[PDF]

    classDef admin fill:#D0021B,stroke:#6B000D,color:#fff
    classDef out fill:#7ED321,stroke:#3B6B00,color:#fff
    class A,B,C,D,E,F,G admin
    class H,H1,H2,H3 out
```
## 12. Permission Matrix
```mermaid
flowchart LR
    subgraph Roles
        CI[Citizen]
        EM[Employer]
        AG[Agency]
        AD[Admin]
    end

    subgraph Permissions
        P1[Browse Jobs]
        P2[Apply for Jobs]
        P3[Post Jobs]
        P4[Post Overseas Jobs]
        P5[Review Applications]
        P6[Verify Employers]
        P7[Verify Agencies]
        P8[Verify Payments]
        P9[Generate Reports]
        P10[Manage Users]
    end

    CI --> P1 & P2
    EM --> P3 & P5
    AG --> P4 & P5
    AD --> P1 & P6 & P7 & P8 & P9 & P10
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 5.0.6 |
| Frontend | Django Templates, Tailwind CSS |
| API | Django REST Framework |
| Database | SQLite (Development) / PostgreSQL (Production) |
| Authentication | JWT, Role-Based Access Control |
| Payments | M-Pesa (Daraja API), eCitizen |
| File Storage | Local (Development) / AWS S3 (Production) |
| Notifications | Email, SMS, Dashboard |

## Prerequisites

- Python 3.10+
- pip
- virtualenv (recommended)
- Git

## Installation

### 1. Clone the Repository

git clone https://github.com/eKidenge/goverment_jobs_portal.git
cd goverment_jobs_portal
2. Create Virtual Environment
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies

pip install -r requirements.txt
4. Environment Variables
Create a .env file in the project root:

env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Optional - for PostgreSQL)
# DB_NAME=gov_jobs_db
# DB_USER=postgres
# DB_PASSWORD=your-password
# DB_HOST=localhost
# DB_PORT=5432

# Email (Optional)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=noreply@governmentjobs.gov

# M-Pesa (Optional)
# MPESA_CONSUMER_KEY=your-key
# MPESA_CONSUMER_SECRET=your-secret
# MPESA_PASSKEY=your-passkey
# MPESA_SHORTCODE=174379

# Site
SITE_URL=http://localhost:8000
ADMIN_EMAIL=admin@governmentjobs.gov
5. Database Setup

# Make migrations
python manage.py makemigrations accounts
python manage.py makemigrations jobs
python manage.py makemigrations payments
python manage.py makemigrations employers
python manage.py makemigrations agencies
python manage.py makemigrations notifications
python manage.py makemigrations admin_panel

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
6. Static Files
# Collect static files
python manage.py collectstatic

# Create media directories (if not exists)
mkdir -p media/documents/cv
mkdir -p media/documents/id
mkdir -p media/documents/passport
mkdir -p media/photos
mkdir -p media/flags
mkdir -p media/employer_logos
mkdir -p media/agency_logos
7. Run Development Server

python manage.py runserver
Access the application at: http://127.0.0.1:8000

Project Structure
text
government_jobs_portal/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── government_jobs_portal/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── forms.py
├── jobs/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── forms.py
├── payments/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── mpesa.py
├── employers/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── agencies/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── admin_panel/
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── notifications/
│   ├── models.py
│   └── views.py
├── static_pages/
│   ├── views.py
│   └── urls.py
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── accounts/
│   ├── jobs/
│   ├── payments/
│   ├── dashboard/
│   └── admin_panel/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/
    └── uploads/
User Types
1. Citizen
Register with personal details and documents

Browse and apply for jobs

Track applications

Make payments for job applications

2. Employer
Register company details

Post job vacancies

Manage applications

Shortlist candidates

3. Recruitment Agency
Register agency details

Post overseas jobs

Manage applicants

Upload contracts

4. Administrator
Full system access

Manage all users, jobs, and payments

Generate reports

System configuration

Payment Integration
Supported Payment Methods
M-Pesa: Integration with Daraja API

eCitizen: Government payment portal

Bank Transfer: Direct bank transfers

Visa/Mastercard: Card payments

Fee Structure
Service	Fee (KES)
Single Job Application	300
Monthly Employment Access	1,000
Quarterly Employment Access	2,500
Reports
Available report types:

Placement Statistics

Jobs by Country

Jobs by Sector

Revenue Report

Labour Migration

User Statistics

Application Statistics

Export formats: CSV, Excel, PDF

Docker Deployment
Build and Run

# Build images
docker-compose build

# Run containers
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
Docker Commands

# View logs
docker-compose logs -f web

# Stop containers
docker-compose down

# Rebuild and restart
docker-compose up -d --build
Testing

# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test jobs

# Run with coverage
pip install coverage
coverage run manage.py test
coverage report
Configuration
Settings Configuration
The project uses environment variables for configuration. Key settings:

DEBUG: Enable/disable debug mode

SECRET_KEY: Django secret key

DATABASES: Database configuration

EMAIL_BACKEND: Email configuration

MPESA_*: M-Pesa payment configuration

Production Settings
For production, update these settings in .env:

env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
Mobile Responsive
The portal is fully responsive and works on:

Desktop browsers

Tablets

Mobile phones

Contributing
Fork the repository

Create a feature branch

Commit your changes

Push to the branch

Create a Pull Request

Guidelines
Follow PEP 8 style guide

Write tests for new features

Update documentation

Use meaningful commit messages

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
Website: https://governmentjobs.go.ke

Email: info@governmentjobs.go.ke

Phone: +254 20 222 0000

Address: Ministry of Labour, Nairobi, Kenya

Acknowledgments
Ministry of Labour, Kenya

Public Employment Service

Accredited Recruitment Agencies

International Employers

Foreign Embassies

Development Partners

Future Enhancements
AI-powered job matching

AI CV analysis

Mobile applications (Android & iOS)

Integration with immigration systems

Digital certificate verification

Labour market analytics dashboard

Multilingual support

Security
JWT authentication

Role-based access control

CSRF protection

SQL injection prevention

XSS protection

Secure password hashing

API Documentation
API endpoints are available at /api/ with JWT authentication.

Example API Endpoints
text
POST /api/accounts/register/ - User registration
POST /api/accounts/login/ - User login
GET  /api/jobs/ - List jobs
GET  /api/jobs/<id>/ - Job details
POST /api/jobs/<id>/apply/ - Apply for job
GET  /api/notifications/ - Get notifications
Status
The project is actively maintained and under continuous development.

Made with ❤️ by the Government of Kenya
