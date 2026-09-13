# Photography Portfolio & Booking Management System

A Python Full Stack internship project built with Flask, SQLite, SQLAlchemy, HTML, CSS and vanilla JavaScript.

## Features

- Responsive photography portfolio
- Portfolio category filtering
- Image lightbox
- Photography packages
- Testimonials
- Contact form
- Booking request system
- Admin authentication
- Admin dashboard
- Gallery CRUD
- Package CRUD
- Testimonial CRUD
- Booking status management
- SQLite database
- Image upload support
- Password hashing
- Server/client-side validation

## Setup

### 1. Create a virtual environment

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python app.py
```

Open http://127.0.0.1:5000

## Admin

Default development credentials:

- Username: `admin`
- Password: `admin123`

For a real deployment, set `ADMIN_PASSWORD` and `SECRET_KEY` environment variables before running.

## Database

The SQLite database `photography.db` is created automatically on first run.

## Project structure

```text
photography_portfolio/
├── app.py
├── requirements.txt
├── README.md
├── photography.db          # created automatically
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   └── uploads/
└── templates/
    ├── base.html
    ├── index.html
    ├── about.html
    ├── portfolio.html
    ├── services.html
    ├── testimonials.html
    ├── contact.html
    ├── booking.html
    ├── 404.html
    ├── auth/login.html
    └── admin/
        ├── dashboard.html
        ├── gallery.html
        ├── packages.html
        ├── testimonials.html
        └── bookings.html
```

## Future enhancements

- Email notifications
- Online payments
- Photographer availability calendar
- Customer accounts
- Photo download galleries
- Cloud image storage
- CSRF protection with Flask-WTF
- Deployment with PostgreSQL
- Analytics dashboard
