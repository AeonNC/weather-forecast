# weather-forecast

A production-ready real-time weather forecast platform built with Django — featuring live WebSocket updates, background task scheduling, AQI data, push notifications, and multi-language support.

**🔗 Live Demo:** [weather-forecast-yve7.onrender.com](https://weather-forecast-yve7.onrender.com)

---

## ✨ Features

- 🌡️ **Real-time weather** — current conditions, 8-day daily forecast, 48-hour hourly forecast
- 🌬️ **Air Quality Index** — PM2.5, NO2, O3, CO with health guidance labels
- ⚡ **WebSocket push** — live weather updates streamed to the browser via Django Channels
- 🔔 **Push notifications** — Firebase Cloud Messaging alerts for severe weather events
- 👤 **User accounts** — JWT auth, per-user preferences (units, language, alert threshold)
- 🕐 **Background tasks** — Celery + Celery Beat refresh all saved locations every 10 minutes
- 📜 **History** — per-location weather snapshot storage with configurable retention

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 4.2, Django REST Framework |
| Auth | JWT (djangorestframework-simplejwt) |
| WebSockets | Django Channels 4, Daphne |
| Task Queue | Celery 5, Celery Beat |
| Cache / Broker | Redis |
| Database | PostgreSQL (prod), SQLite (dev) |
| Weather API | Open-Meteo (free, no API key) |
| Push Notifications | Firebase Admin SDK |
| Static Files | WhiteNoise + Brotli |
| Deployment | Render |

---

## 🏗️ Architecture

```
Browser
  │
  ├── HTTPS ──► Gunicorn/Daphne (ASGI)
  │                   │
  │            ┌──────┴──────┐
  │            ▼             ▼
  │       Django Views   Django Channels
  │       (REST API)     (WebSocket)
  │
  └── WS ──► Real-time weather stream
                   │
             Redis (cache · channel layer · Celery broker)
                   │
         ┌─────────┴──────────┐
         ▼                    ▼
   Celery Worker         Celery Beat
 (refresh weather)   (every 10 min schedule)
         │
   Open-Meteo API (forecast + AQI + geocoding)
         │
   PostgreSQL (snapshots · forecasts · alerts)
```

---

## 🚀 Getting Started (Local)

### Prerequisites
- Python 3.12+
- Redis running on `localhost:6379`

### 1 — Clone & install

```bash
git clone https://github.com/yourusername/weather-forecast.git
cd weather-forecast
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2 — Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://127.0.0.1:6379
CORS_ALLOWED_ORIGINS=http://localhost:8000
FIREBASE_CREDENTIALS_PATH=firebase.json   # optional
```

### 3 — Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4 — Run

```bash
# Terminal 1 — Web server
python manage.py runserver

# Terminal 2 — Celery worker (optional, for background refresh)
celery -A config.celery worker --loglevel=info

# Terminal 3 — Celery Beat scheduler (optional)
celery -A config.celery beat --loglevel=info
```

Visit `http://localhost:8000`

---

## 📡 API Reference

All weather endpoints are public (`AllowAny`). Auth endpoints require a JWT Bearer token.

### Weather

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/weather/full/?lat=&lon=` | Current + forecast + AQI + alerts + lifestyle advice |
| GET | `/api/weather/current/?lat=&lon=` | Current conditions only |
| GET | `/api/weather/forecast/?lat=&lon=&days=7` | Daily + hourly forecast |
| GET | `/api/weather/aqi/?lat=&lon=` | Air quality index |
| GET | `/api/weather/alerts/?lat=&lon=` | Severe weather alerts |
| GET | `/api/weather/search/?q=London` | Forward geocoding |
| GET | `/api/weather/reverse-geocode/?lat=&lon=` | Reverse geocoding |
| GET | `/api/weather/history/?location_id=` | Stored snapshots (auth required) |

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Create account |
| POST | `/api/auth/login/` | Get JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| POST | `/api/auth/logout/` | Blacklist refresh token |
| GET | `/api/auth/me/` | Current user info |
| PATCH | `/api/auth/preferences/` | Update units, language, alerts |

### Locations

| Method | Endpoint | Description |
|---|---|---|
| GET / POST | `/api/locations/` | List or create locations |
| GET / PATCH / DELETE | `/api/locations/<id>/` | Manage a location |
| PATCH | `/api/locations/<id>/default/` | Set as default |

### WebSocket

```
ws://yourhost/ws/weather/<location_id>/
```

Messages sent by server:
```json
{ "type": "weather_update", "data": { ... } }
{ "type": "severe_alert",   "alert": { ... } }
{ "type": "connected",      "message": "Real-time weather stream active." }
```

### Health Check

```
GET /health/   →   {"status": "ok"}
```

---

## 🌍 Deployment (Render)

1. Push to GitHub and connect your repo in [Render](https://render.com)
2. Add a **PostgreSQL** database — `DATABASE_URL` is injected automatically
3. Add a **Redis** instance — `REDIS_URL` is injected automatically
4. Set environment variables:

| Variable | Value |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `DJANGO_SECRET_KEY` | _(generate a secure key)_ |
| `ALLOWED_HOSTS` | `yourapp.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | `https://yourapp.onrender.com` |

5. Run migrations via Render Shell:
```bash
python manage.py migrate
python manage.py createsuperuser
```

For Celery, add a separate **Background Worker** service with start command:
```
celery -A config.celery worker --loglevel=info
```

---

## 📁 Project Structure

```
weather-forecast/
├── apps/
│   ├── core/            # Custom exception handler, utilities
│   ├── users/           # Custom user model, JWT auth, preferences
│   ├── locations/       # Saved locations per user
│   ├── weather/
│   │   ├── services/
│   │   │   ├── openmeteo.py   # Open-Meteo API wrapper
│   │   │   ├── aqi.py         # AQI enrichment
│   │   │   └── alerts.py      # Alert severity mapping
│   │   ├── consumers.py       # WebSocket consumer
│   │   ├── tasks.py           # Celery background tasks
│   │   ├── models.py          # Snapshots, forecasts, alerts
│   │   └── views.py           # REST API views
│   └── notifications/   # FCM push notification tasks
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── asgi.py          # ASGI + Channels routing
│   └── celery.py        # Celery app + beat schedule
├── frontend/
│   ├── templates/       # Django HTML templates
│   └── static/          # CSS, JS, PWA manifest
├── docker/              # Dockerfile, docker-compose, nginx
├── requirements.txt
├── Procfile             # Render/Railway process config
└── manage.py
```

---

## 📄 License

MIT License — free to use, modify and distribute.