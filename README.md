<div align="center">

# 🚀 Event Management Platform

A modular Django REST API for managing the full event lifecycle — from organizer planning and stage management to participant registration, result publishing, and feedback collection.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.1-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![DRF](https://img.shields.io/badge/Django%20REST-API-FF1709?style=for-the-badge)
![JWT](https://img.shields.io/badge/JWT-Authentication-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

</div>

---

## ✨ Overview

This project is built as a Django monolith with a REST API layer and multiple domain modules. It supports:

- Event creation and lifecycle management
- Organizer and participant roles
- Public and organizer-only views
- Stage and assignment management
- Event attribute metadata
- Registration workflows
- Result publishing and feedback collection
- JWT-based authentication and OpenAPI schema generation

---

## 🧱 Tech Stack

| Layer            | Technology            |
| ---------------- | --------------------- |
| Language         | Python 3.10+          |
| Framework        | Django 6.1            |
| API              | Django REST Framework |
| Auth             | Simple JWT            |
| Database         | PostgreSQL            |
| Background tasks | Celery + Redis        |
| API docs         | drf-spectacular       |
| Admin UI         | django-unfold         |
| Audit trail      | django-auditlog       |

---

## ⚙️ Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Redis
- virtualenv / venv
- Docker and Docker Compose (optional, for containerized setup)

### 1. Clone repository

```bash
git clone <repo-url>
cd event-management-platform
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
SECRET_KEY=replace-with-strong-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=event_management
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

> The project reads configuration from the Django settings package, including environment-sensitive files under `config/settings/`.

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Start the app

```bash
python manage.py runserver
```

Then open:

- App: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

### Docker workflow

```bash
docker compose up --build
```

This project includes `docker-compose.yml`, `Dockerfile`, and `Dockerfile.nginx` for containerized local development.

---

## 🗂️ Project Structure

```text
.
├── accounts/                 # Authentication, registration, JWT login/logout
├── attributes/               # Shared attribute definitions and event attribute values
├── config/                   # Django settings, URLs, Celery, and app config
├── core/                     # Shared permissions, helpers, and common logic
├── events/                   # Events, stages, stage assignments, and event metadata
├── registrations/            # Participant registration logic for events/stages
├── results/                  # Result publishing and participant feedback
├── users/                    # Profiles and audit log endpoints
├── static/                   # Static files
├── staticfiles/              # Collected static output
├── manage.py                 # Django management entry point
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Local development services
├── Dockerfile                # App container
├── Dockerfile.nginx          # Nginx container
├── README.md                 # Project documentation
├── .env.example              # Optional example env file
└── ...
```

---

## 🧪 Development Commands

```bash
python manage.py test
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

Celery worker:

```bash
celery -A config worker -l info
```

Celery beat:

```bash
celery -A config beat -l info
```

---

## 📚 API Documentation

The API is mounted under the `/api/` namespace. OpenAPI schema is exposed through the Django REST Framework schema generator.

### Documentation routes

- Schema: `/api/schema/`
- Swagger UI: `/api/schema/swagger-ui/`
- Redoc UI: `/api/schema/redoc/`

### Authentication

All protected endpoints use JWT authentication via `Authorization: Bearer <token>`.

| Endpoint              | Method | Access        | Description                             |
| --------------------- | ------ | ------------- | --------------------------------------- |
| `/api/auth/register/` | POST   | Public        | Register a new user                     |
| `/api/auth/login/`    | POST   | Public        | Login and receive access/refresh tokens |
| `/api/auth/refresh/`  | POST   | Public        | Refresh JWT access token                |
| `/api/auth/logout/`   | POST   | Authenticated | Revoke the refresh token                |
| `/api/token/`         | POST   | Public        | Obtain JWT pair                         |
| `/api/token/refresh/` | POST   | Public        | Refresh access token                    |

### User profiles and audit logs

| Endpoint                     | Method                   | Access        | Description                 |
| ---------------------------- | ------------------------ | ------------- | --------------------------- |
| `/api/participant-profiles/` | GET, POST, PATCH, DELETE | Authenticated | Manage participant profiles |
| `/api/organizer-profiles/`   | GET, POST, PATCH, DELETE | Authenticated | Manage organizer profiles   |
| `/api/audit-logs/`           | GET                      | Authenticated | View audit history          |

### Event catalog and organizer events

| Endpoint                                                                          | Method                  | Access    | Description                |
| --------------------------------------------------------------------------------- | ----------------------- | --------- | -------------------------- |
| `/api/event-types/`                                                               | GET                     | Public    | Event type catalog         |
| `/api/stage-role-types/`                                                          | GET                     | Public    | Stage role definitions     |
| `/api/public/events/`                                                             | GET                     | Public    | Published events list      |
| `/api/public/events/{event_pk}/`                                                  | GET                     | Public    | Published event detail     |
| `/api/organizer/events/`                                                          | GET, POST               | Organizer | Organizer-owned events     |
| `/api/organizer/events/{event_pk}/`                                               | GET, PUT, PATCH, DELETE | Organizer | Event detail/update/delete |
| `/api/organizer/events/{event_pk}/stages/`                                        | GET, POST               | Organizer | Event stages               |
| `/api/organizer/events/{event_pk}/stages/{stage_pk}/`                             | GET, PUT, PATCH, DELETE | Organizer | Stage detail/update/delete |
| `/api/organizer/events/{event_pk}/stages/{stage_pk}/assignments/`                 | GET, POST               | Organizer | Stage assignments          |
| `/api/organizer/events/{event_pk}/stages/{stage_pk}/assignments/{assignment_pk}/` | GET, PUT, PATCH, DELETE | Organizer | Assignment detail          |

### Attributes

| Endpoint                                             | Method                   | Access                               | Description                        |
| ---------------------------------------------------- | ------------------------ | ------------------------------------ | ---------------------------------- |
| `/api/attributes/`                                   | GET, POST, PATCH, DELETE | Public for read, Organizer for write | Shared attribute metadata          |
| `/api/public/events/{event_pk}/attribute-values/`    | GET                      | Public                               | Published event attributes         |
| `/api/organizer/events/{event_pk}/attribute-values/` | GET, POST                | Organizer                            | Organizer-managed event attributes |

### Registrations

| Endpoint                                          | Method    | Access      | Description                              |
| ------------------------------------------------- | --------- | ----------- | ---------------------------------------- |
| `/api/registrations/`                             | GET, POST | Participant | List/create participant registrations    |
| `/api/registrations/{registration_pk}/`           | GET       | Participant | Registration detail                      |
| `/api/registrations/{registration_pk}/cancel/`    | POST      | Participant | Cancel a registration                    |
| `/api/organizer/events/{event_pk}/registrations/` | GET       | Organizer   | Registrations for organizer-owned events |

### Results and feedback

| Endpoint                                                     | Method                        | Access      | Description                                  |
| ------------------------------------------------------------ | ----------------------------- | ----------- | -------------------------------------------- |
| `/api/public/events/{event_pk}/results/`                     | GET                           | Public      | Published results for an event               |
| `/api/organizer/events/{event_pk}/results/`                  | GET, POST, PUT, PATCH, DELETE | Organizer   | Manage event results                         |
| `/api/organizer/events/{event_pk}/feedbacks/`                | GET                           | Organizer   | View feedback for an event                   |
| `/api/participant/registrations/{registration_pk}/feedback/` | GET, POST                     | Participant | Read or submit feedback for own registration |

---

## 🔐 API Usage Examples

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "password": "secret123"
  }'
```

### Create event (authenticated organizer)

```bash
curl -X POST http://127.0.0.1:8000/api/organizer/events/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Summer Festival 2026",
    "description": "Annual event",
    "event_type": 1,
    "start_time": "2026-07-10T10:00:00Z",
    "end_time": "2026-07-10T18:00:00Z",
    "status": "draft"
  }'
```

### Register for an event

```bash
curl -X POST http://127.0.0.1:8000/api/registrations/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "event": 1,
    "stage": 2
  }'
```

---

## 🛡️ Business Rules

The system enforces validation rules to keep the platform consistent:

- Event end time must be later than the start time
- Registration must match the event and permitted stage configuration
- Results can only be published for completed events
- Feedback ratings must be within the valid range
- Stage assignments must belong to the correct event
- Attribute values must match the declared attribute type

---

## 📦 Environment & Deployment

The settings are separated by environment:

- `config/settings/base.py` — shared configurations
- `config/settings/dev.py` — local development settings
- `config/settings/prod.py` — production settings

For production deployment, ensure:

- secure `SECRET_KEY`
- `DEBUG=False`
- valid `ALLOWED_HOSTS`
- PostgreSQL and Redis connection settings are correct
- static/media files are served properly

---

## 🧭 Architecture Summary

The project follows a modular monolith pattern:

- `accounts` — authentication, user creation, auth flows
- `users` — profile and audit APIs
- `events` — event lifecycle and stage management
- `attributes` — reusable metadata definitions and values
- `registrations` — participant actions and organizer visibility
- `results` — result publication and feedback workflows
- `core` — permissions and shared logic

This structure keeps business logic separated while still remaining easy to run and maintain as a single Django application.

---

## 🤝 Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repository
2. Create a branch for the change
3. Implement and test the feature
4. Commit cleanly and open a pull request

---

## 📄 License

This project does not include a dedicated license file yet. If you plan to distribute it publicly, add an appropriate open-source license such as MIT.

---

<div align="center">

Built with Django and the Django REST Framework for modern event management systems.

</div>
