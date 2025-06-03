# MicroAnalitycs

This repository provides a minimal skeleton for the MicroAnalitycs project described in the planning document. It includes a FastAPI backend, a Streamlit frontend, simple machine learning models and placeholder chatbot integration.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To run the backend:

```bash
uvicorn backend.app:app --reload
```

To run the frontend:

```bash
streamlit run frontend/app.py
```

A PostgreSQL database can be configured with the `DATABASE_URL` environment variable. By default an in-memory SQLite database is used.
