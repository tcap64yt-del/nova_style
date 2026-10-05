# Nova Style

Nova Style is a Django-based e-commerce web application that provides a complete shopping workflow for customers along with product, order, coupon, offer, and sales management features for staff and administrators.

## Features

### Customer Features

- User registration and authentication
- User login and logout
- Password reset functionality
- Product browsing
- Product categories
- Product variants
- Product images
- Product offers
- Category offers
- Shopping cart
- Wishlist
- Address management
- Coupon usage
- Order placement
- Order tracking
- Order cancellation
- Order returns
- Wallet functionality
- Wallet transactions
- Razorpay payment integration
- Payment failure handling
- Payment retry
- Product reviews
- Referral functionality

### Staff / Admin Features

- Staff authentication
- Staff dashboard
- Product management
- Product variant management
- Product image management
- Category management
- Product offers
- Category offers
- Coupon management
- Order management
- Order status management
- Order return management
- Sales reports
- Top-selling products
- Top-selling categories
- Exporting reports to Excel
- Generating PDF reports

## Technology Stack

### Backend

- Python
- Django
- Django Allauth
- PostgreSQL

### Frontend

- HTML
- CSS
- JavaScript
- Bootstrap

### Third-Party Services and Libraries

- Razorpay — payment processing
- Cloudinary — media/image storage
- ReportLab — PDF report generation
- OpenPyXL — Excel report generation
- python-dotenv — environment variable management

## Project Structure

```text
nova_style/
│
├── cart/
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── coupon/
│   ├── migrations/
│   ├── models.py
│   └── ...
│
├── nova_style/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── order/
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── product/
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── staff/
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── user/
│   ├── migrations/
│   ├── adapters.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── static/
│   └── css/
│
├── templates/
│
├── manage.py
├── requirements.txt
└── .env.example
```

## Requirements

Before running the project, make sure you have:

- Python 3.13 or a compatible Python version
- PostgreSQL
- Git
- A Razorpay account for payment functionality
- A Cloudinary account for media storage

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/tcap64yt-del/nova_style.git
cd nova_style
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file from `.env.example`.

#### Git Bash

```bash
cp .env.example .env
```

Then open `.env` and provide your local configuration and service credentials.

Example:

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=your-email

RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret

DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-cloudinary-key
CLOUDINARY_API_SECRET=your-cloudinary-secret
```

**Never commit `.env` or any file containing real credentials.**

## Environment Variables

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DJANGO_ALLOWED_HOSTS` | Hosts allowed by Django |
| `EMAIL_HOST_USER` | Email account used by the application |
| `EMAIL_HOST_PASSWORD` | Email account password |
| `DEFAULT_FROM_EMAIL` | Default email sender |
| `RAZORPAY_KEY_ID` | Razorpay API key |
| `RAZORPAY_KEY_SECRET` | Razorpay API secret |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL database user |
| `DB_PASSWORD` | PostgreSQL database password |
| `DB_HOST` | PostgreSQL database host |
| `DB_PORT` | PostgreSQL database port |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |

## Database Setup

Create a PostgreSQL database and configure its credentials in `.env`.

For example:

```env
DB_NAME=nova_style
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

After configuring the database, run the migrations:

```bash
python manage.py migrate
```

## Create an Admin User

Create a Django superuser:

```bash
python manage.py createsuperuser
```

Follow the prompts to configure the administrator account.

## Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The application will normally be available at:

```text
http://127.0.0.1:8000/
```

## Django Checks

To verify the Django configuration:

```bash
python manage.py check
```

## Database Migrations

Create migrations after model changes:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

## Payments

Nova Style integrates Razorpay for online payment processing.

Razorpay credentials are configured through environment variables:

```env
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
```

Payment-related functionality includes:

- Payment creation
- Payment status handling
- Payment failure handling
- Payment retry
- Razorpay payment identifiers

## Media Storage

Cloudinary is used for media/image storage.

Configure Cloudinary through:

```env
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

## Reports

The staff dashboard includes reporting functionality.

### Excel Reports

Excel reports are generated using OpenPyXL.

### PDF Reports

PDF reports are generated using ReportLab.

The reporting functionality includes sales information and top-selling products and categories.

## Static Files

Static assets are stored in the `static/` directory.

Templates are stored in the `templates/` directory.

During development, Django serves static files according to the project's configured settings.

## Security

Sensitive configuration is loaded through environment variables.

The following files should not be committed:

```text
.env
*.env
```

Python-generated cache files are also excluded from Git:

```text
__pycache__/
*.pyc
```

Use `.env.example` as a template for configuring a local development environment.

## Git Workflow

Check the current repository status:

```bash
git status
```

Create a feature or fix branch when appropriate:

```bash
git checkout -b feature/your-feature
```

Stage changes:

```bash
git add .
```

Commit changes:

```bash
git commit -m "Describe your change"
```

Push the branch:

```bash
git push origin feature/your-feature
```

## Development Notes

Keep secrets and environment-specific configuration outside the repository.

Do not commit:

- `.env`
- API keys
- Database passwords
- Payment credentials
- Cloudinary secrets
- Python cache files
- Virtual environments

Use `.env.example` to document the environment variables required by the application without exposing their values.