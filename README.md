# MicroAnalitycs

This repository provides a minimal skeleton for the MicroAnalitycs project described in the planning document. It includes a FastAPI backend, a Streamlit frontend, simple machine learning models and placeholder chatbot integration.

## Tecnologías

### Base de Datos
- SQLite (por defecto)
- PostgreSQL (configurable via `DATABASE_URL`)
- SQLAlchemy como ORM

### Backend
- FastAPI como framework web
- Estructura modular:
  - Modelos SQLAlchemy
  - Schemas Pydantic 
  - CRUD operations

### Frontend
- Streamlit para interfaz de usuario
- Comunicación con backend via REST API

### Machine Learning
- scikit-learn para modelos predictivos
- Regresión lineal para predicción de demanda

## Estructura del Proyecto
```
backend/
  ├── models/     # Modelos SQLAlchemy
  ├── schemas/    # Schemas Pydantic
  ├── crud/       # Operaciones CRUD
  └── app.py      # Aplicación FastAPI

frontend/
  └── app.py      # Interfaz Streamlit

models/
  ├── train_regresion.py  # Entrenamiento
  └── predict.py          # Predicciones

chatbot/         # Integración chatbot
scraping/        # Web scraping
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
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