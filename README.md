<div align="center">

# 🚀 Event-Planet

A modern Django REST API for managing the full lifecycle of events — from planning and registration to stage operations, results, and feedback.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.1-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-REST%20API-FF1709?style=for-the-badge)
![JWT](https://img.shields.io/badge/JWT-Authentication-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

</div>

---

## ✨ Features

- 🎯 **Event lifecycle management** — create, publish, close, and finish events with validation rules.
- 🧑‍🤝‍🧑 **User and role management** — custom phone-based authentication with organizer, participant, and staff roles.
- 🏟️ **Stage-based scheduling** — manage stages, order them, assign guests, and track capacity.
- 📝 **Dynamic attributes** — attach typed custom attributes to different event types.
- 🎟️ **Registration system** — handle event-level and stage-level registrations with strict validation.
- 📊 **Results and rankings** — publish results with rank or score data after an event is completed.
- 💬 **Feedback collection** — gather participant ratings and comments after finished events.
- 🔐 **Secure APIs** — JWT authentication, throttling, schema generation, and API docs.
- 📚 **Admin-ready platform** — integrated admin dashboard and OpenAPI documentation via Swagger/Redoc.

---

## 🧱 Tech Stack

| Layer         | Technology            |
| ------------- | --------------------- |
| Language      | Python 3.10+          |
| Framework     | Django 6.1            |
| API           | Django REST Framework |
| Auth          | JWT (Simple JWT)      |
| Database      | PostgreSQL            |
| Cache / queue | Redis + Celery        |
| Docs          | drf-spectacular       |
| Admin         | django-unfold         |
| Audit         | django-auditlog       |

---

## ⚙️ Installation & Setup

### 1. Prerequisites

- Python 3.10+
- PostgreSQL installed and running
- Redis installed and running
- Virtual environment support (`venv` / `virtualenv`)

### 2. Clone the repository

```bash
git clone https://github.com/ostans/event-management-platform.git
cd event-management-platform
```

### 3. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
# .venv\Scripts\activate   # Windows
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
NAME=event_planet
PGUSER=postgres
PASSWORD=postgres
HOST=localhost
PORT=5432
```

> This project uses `python-decouple` to read the environment values from the settings configuration.

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

### 8. Run the server

```bash
python manage.py runserver
```

Open the project in the browser:

- http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

---

## 🗄️ Project Structure

```text
.
├── accounts/                  # Custom user model and auth APIs
├── attributes/                # Dynamic event attributes and typed values
├── config/                    # Django settings, URLs, ASGI/WSGI, Celery config
├── core/                      # Shared base models and permissions
├── events/                    # Events, stages, and stage assignments
├── registrations/             # Event/stage registration logic
├── results/                   # Results and feedback logic
├── static/                    # Static files
├── staticfiles/               # Collected static files
├── users/                     # User-focused logic and APIs
├── .gitignore
├── manage.py
├── requirements.txt
├── README.md
└── ...
```

---

## 🚀 API Overview

The API is served under the `/api/` namespace.

### Authentication

| Endpoint              | Method | Description              |
| --------------------- | ------ | ------------------------ |
| `/api/auth/register/` | POST   | Register a new user      |
| `/api/auth/login/`    | POST   | Login and get JWT tokens |
| `/api/auth/refresh/`  | POST   | Refresh access token     |
| `/api/auth/logout/`   | POST   | Logout user session      |
| `/api/token/`         | POST   | Obtain JWT pair          |
| `/api/token/refresh/` | POST   | Refresh JWT token        |

### API Documentation

- Schema: `/api/schema/`
- Swagger UI: `/api/schema/swagger-ui/`
- Redoc: `/api/schema/redoc/`

### Main domain APIs

- Event types and event management
- Organizer event dashboards and nested stage endpoints
- Registration endpoints for participants
- Result and ranking APIs
- Dynamic attribute endpoints by event type

---

## 🧪 Development Workflow

### Run tests

```bash
python manage.py test
```

### Create migrations

```bash
python manage.py makemigrations
```

### Apply migrations

```bash
python manage.py migrate
```

### Collect static files

```bash
python manage.py collectstatic
```

---

## 🔄 Celery & Redis

This project includes Celery integration for background work and async processing. To run the worker locally:

```bash
celery -A config worker -l info
```

To run the scheduler:

```bash
celery -A config beat -l info
```

---

## 🛡️ Validation & Business Rules

The platform enforces several important rules:

- Event end time must be after start time
- Registration scope must match the event configuration
- Result publication is allowed only for finished events
- Ratings must be between 1 and 5
- Stage assignments must belong to the correct event
- Attribute values must match the declared data type

These validations are enforced in the model layer to keep the data consistent and reliable.

---

## 📦 Environment Configuration

The settings are split by environment:

- `config/settings/base.py` — shared defaults
- `config/settings/dev.py` — local development settings
- `config/settings/prod.py` — production deployment settings

For production, make sure to configure:

- strong `SECRET_KEY`
- `DEBUG=False`
- valid `ALLOWED_HOSTS`
- secure PostgreSQL and Redis connection settings

---

## 🧭 Architecture Overview

The project follows a modular Django monolith pattern:

- **accounts** — user identity, custom authentication, and profile-related logic
- **users** — user-facing app logic and endpoints
- **events** — event creation, stage scheduling, and assignment handling
- **attributes** — typed metadata for events
- **registrations** — participant enrollment logic
- **results** — results, scores, ranks, and feedback
- **core** — shared models and reusable rules

This separation makes the system easier to expand with new features such as payments, notifications, QR check-ins, analytics, and admin reporting.

---

## 📄 License

This project does not currently include a dedicated license file. If you plan to share or distribute the project publicly, it is recommended to add a license such as MIT or GPL.

---

## 🤝 Contributing

Contributions are welcome. A typical workflow is:

1. Fork the repository
2. Create a feature branch
3. Implement and test your changes
4. Open a pull request with a clear summary

---

<div align="center">

Built with Django and the Django REST Framework to power modern event management experiences.

</div>
