# Blue Clinic - AI-Powered Smart Appointment System

Blue Clinic is a full-stack clinic appointment application with an AI clinical assistant, patient appointment booking, session-based chat history, and an admin dashboard for managing clinic appointments.

Patients can describe symptoms in natural language, receive guidance from the AI assistant, and continue to the appointment flow when a department is suggested. Clinic administrators can view, filter, approve, cancel, delete, and export appointment records.

## Table of Contents

- [About the Project](#about-the-project)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Features](#features)
- [API Overview](#api-overview)
- [Running Tests](#running-tests)
- [Contribution Guidelines](#contribution-guidelines)
- [Developers](#developers)

## About the Project

Blue Clinic modernizes the appointment workflow for small and medium-sized clinics. The system combines a React frontend, a FastAPI backend, SQLite persistence, JWT authentication, appointment conflict prevention, and a Gemini-powered AI assistant with retrieval-augmented generation.

The project focuses on:

- Reducing manual appointment handling.
- Preventing double-booked doctor time slots.
- Helping patients reach the right department faster.
- Giving administrators a clear dashboard for daily clinic operations.

### Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | React, React Router, Vanilla CSS |
| Backend | FastAPI, SQLAlchemy, SQLite |
| AI / LLM | Google Gemini, LangChain, RAG, Qdrant local vector store |
| Authentication | JWT, python-jose, bcrypt |
| Tooling | Docker, Docker Compose, pytest, ruff |

## Requirements

### Option A - Docker

Install Docker Desktop 24.0 or higher. Docker includes both the Docker engine and Docker Compose.

### Option B - Manual Setup

Install the following tools:

- Python 3.12 or higher
- Node.js 18.0 or higher
- npm 9.0 or higher
- Git 2.40 or higher

Check versions:

```bash
python --version
node --version
npm --version
git --version
docker --version
```

## Project Structure

```text
ClinicAppointment/
├── app/                    # FastAPI application package
│   ├── main.py             # API entry point and route definitions
│   ├── models.py           # Pydantic request/response models
│   ├── db_models.py        # SQLAlchemy database models
│   ├── services/           # AI, auth, sessions, appointment, RAG services
│   └── middleware/         # Logging and rate limiting middleware
├── data/                   # SQLite database file, created at runtime
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # Shared UI components
│   │   ├── pages/          # Home, appointments, admin, AI assistant pages
│   │   └── services/       # Frontend API clients
│   └── package.json
├── scripts/                # Utility and evaluation scripts
├── tests/                  # Pytest test suite
├── .env.example            # Environment variable template
├── docker-compose.yml      # Multi-service container definition
├── Dockerfile              # Backend container image
└── requirements.txt        # Python dependencies
```

## Installation

### Option A - Docker

1. Clone the repository:

```bash
git clone https://github.com/ahmedfarukons/ClinicAppointment.git
cd ClinicAppointment
```

2. Create an environment file:

```bash
cp .env.example .env
```

3. Add your Gemini API key to `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

You can create a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey). The application can start without a key, but AI responses require a valid key.

4. Build and start the services:

```bash
docker compose up -d --build
```

5. Open the application:

| Service | URL |
| --- | --- |
| Patient interface | `http://localhost:3000` |
| Backend API | `http://localhost:8000` |
| API documentation | `http://localhost:8000/docs` |
| Admin panel | `http://localhost:3000/admin/login` |

Stop the application:

```bash
docker compose down
```

### Option B - Manual Setup

1. Clone the repository:

```bash
git clone https://github.com/ahmedfarukons/ClinicAppointment.git
cd ClinicAppointment
```

2. Create and activate a Python virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

5. Create your environment file:

```bash
cp .env.example .env
```

6. Start the backend:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

7. In a second terminal, start the frontend:

```bash
cd frontend
npm start
```

The frontend runs at `http://localhost:3000` and proxies API requests to `http://127.0.0.1:8000`.

## Configuration

All environment variables are loaded from `.env`.

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `GEMINI_API_KEY` | Yes for AI responses | - | Google Gemini API key. |
| `LLM_MODEL` | No | `gemini-1.5-flash` | Gemini model used by the assistant. |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` | Sentence transformer model for retrieval. |
| `QDRANT_PATH` | No | `./qdrant_data` | Local Qdrant vector store path. |
| `COLLECTION_NAME` | No | `chatdoctor` | Qdrant collection name. |
| `CHUNK_SIZE` | No | `512` | Text chunk size for retrieval. |
| `CHUNK_OVERLAP` | No | `64` | Overlap between text chunks. |
| `DATABASE_PATH` | No | `./data/chatdoctor.db` | SQLite database path. |
| `JWT_SECRET` | Yes in production | `change-me-in-production-use-a-random-string` | Secret key for signing JWT tokens. |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm. |
| `JWT_EXPIRE_MINUTES` | No | `480` | Token lifetime in minutes. |
| `RATE_LIMIT` | No | `30/minute` | API rate limit per client. |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity. |

Never commit a real `.env` file to version control.

## Usage

### Patient Workflow

1. Open `http://localhost:3000`.
2. Create an account or sign in to the AI assistant.
3. Ask a medical question or describe symptoms.
4. If the assistant suggests a department, continue to the appointment page.
5. Select a department, doctor, date, and time slot.
6. Submit the appointment form.

### Admin Workflow

1. Open `http://localhost:3000/admin/login`.
2. Sign in with the default local credentials:

```text
Username: admin
Password: clinic2024
```

3. Manage appointments from the admin dashboard.

Change the admin credentials before using the system outside local development.

## Features

### Patient Side

- AI clinical assistant with session-based chat history.
- English AI responses with medical safety disclaimers.
- Department suggestion based on symptoms or appointment intent.
- Appointment form with department, doctor, date, and time selection.
- Conflict prevention for already booked doctor time slots.
- Responsive user interface for desktop and mobile screens.

### Admin Side

- Admin login with token-based authentication.
- Appointment table with filters and search.
- Appointment status updates: pending, confirmed, cancelled.
- Appointment deletion.
- CSV export for appointment records.
- Dashboard statistics by date, department, and status.

### System

- FastAPI backend with structured JSON logging.
- SQLite database through SQLAlchemy.
- JWT authentication for protected user and admin flows.
- Rate limiting with slowapi.
- RAG pipeline with local Qdrant storage and multi-source retrieval.
- Explainable AI metadata including route, confidence, decision steps, and sources.

## API Overview

Interactive API documentation is available at `http://localhost:8000/docs` when the backend is running.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check. |
| `POST` | `/auth/register` | Register a user and receive a JWT token. |
| `POST` | `/auth/login` | Log in and receive a JWT token. |
| `GET` | `/sessions` | List authenticated user's chat sessions. |
| `POST` | `/sessions` | Create a new chat session. |
| `GET` | `/sessions/{session_id}/messages` | List messages in a chat session. |
| `DELETE` | `/sessions/{session_id}` | Delete a chat session. |
| `POST` | `/chat` | Send a message to the AI assistant. |
| `GET` | `/api/appointments` | List public appointments with optional filters. |
| `POST` | `/api/appointments` | Create an appointment. |
| `POST` | `/admin/login` | Admin login. |
| `GET` | `/admin/stats` | Admin dashboard statistics. |
| `GET` | `/admin/appointments` | List appointments for admin management. |
| `PATCH` | `/admin/appointments/{appt_id}/status` | Update appointment status. |
| `DELETE` | `/admin/appointments/{appt_id}` | Delete an appointment. |

## Running Tests

Run all backend tests:

```bash
pytest tests/ -v
```

Run a specific test file:

```bash
pytest tests/test_auth.py -v
pytest tests/test_session.py -v
pytest tests/test_intent_and_appointment.py -v
```

Run linting:

```bash
ruff check .
```

## Contribution Guidelines

1. Create a new branch for your change:

```bash
git checkout -b fix/short-description
```

2. Keep commits small and focused.
3. Add or update tests when behavior changes.
4. Run tests before opening a pull request:

```bash
pytest tests/ -v
```

5. Use clear commit messages, for example:

```bash
git commit -m "fix: prevent duplicate appointment slots"
git commit -m "feat: add admin appointment export"
git commit -m "docs: update setup instructions"
```

## Developers

- Ahmed Faruk Onuş
- Çağrı Demir
- Mehmet Emin Miran
- Ufuk Gülten
- Azad Karadağ
