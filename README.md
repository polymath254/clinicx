# ClinicX API

**ClinicX API** is a modern Django backend for managing customers, orders, and SMS notifications.  
It features JWT-secured endpoints, background task processing with Celery, and seamless SMS integration via Africa's Talking.

---

## Features

- **Django REST API** for Customers & Orders
- **JWT Authentication** (stateless, secure)
- **Async SMS notifications** (Celery + Redis)
- **Africa’s Talking SMS Integration**
- **Automated tests** (unit and integration)
- **CI/CD** with GitHub Actions
- **Dockerized** for easy development and deployment

---

## Project Structure

```

clinicx-app/
│
├── clinicx/               # Project config, Celery setup
├── customers/             # Customers API app
├── orders/                # Orders API app
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
├── .env                   # Not tracked in git!
└── README.md

````

---

## Getting Started

### 1. Clone this repository

```bash
git clone https://github.com/polymath254/clinicx-app.git
cd clinicx-app
````

### 2. Set up your `.env` file

Copy `.env.example` to `.env` and set your secrets:

```
DJANGO_SECRET_KEY=changeme
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your_key
```

### 3. Build & run with Docker Compose

```bash
docker compose up --build
```

* Django API: [http://localhost:8000](http://localhost:8000)
* Celery & Redis are managed automatically

---

## Development Without Docker

```bash
python -m venv venv
source venv/bin/activate    # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

*(Start Redis separately with `redis-server` if running locally)*

---

## Authentication

* Obtain a token:
  `POST /api/token/` with your username & password
  (returns an `access` and `refresh` token)
* Use in header for all requests:

  ```
  Authorization: Bearer <access_token>
  ```

---

## API Endpoints

| Endpoint               | Methods          | Description              |
| ---------------------- | ---------------- | ------------------------ |
| `/api/customers/`      | GET,POST         | List or create customers |
| `/api/customers/<id>/` | GET,PATCH,DELETE | Retrieve, update, delete |
| `/api/orders/`         | GET,POST         | List or create orders    |
| `/api/orders/<id>/`    | GET,PATCH,DELETE | Retrieve, update, delete |
| `/api/token/`          | POST             | Get JWT token            |
| `/api/token/refresh/`  | POST             | Refresh JWT token        |

---

## Testing

```bash
python manage.py test
```

*(Or use `coverage run manage.py test` then `coverage report` for coverage details)*

---

## Tech Stack

* Python, Django, Django REST Framework
* Celery, Redis
* Africa’s Talking SDK
* Docker & Docker Compose
* GitHub Actions

---

## Notes

* SMS works for Africa’s Talking sandbox numbers only during development.
* For production, set `DEBUG=False`, update `ALLOWED_HOSTS`, and use a production server.

---

## Author

**Evans Kaila**
[your.kailaevans254@gmail.com](kailaevans254@gmail.com)
[GitHub: polymath254](https://github.com/polymath254)



