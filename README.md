# MicroAnalitycs

Proyecto de analítica predictiva que integra un scraper, un modelo de regresión
de demanda y una API. El público objetivo son analistas de negocio que requieren
predicciones rápidas. El éxito se mide por la precisión del modelo (R² ≥ 0.8),
la rapidez del bot (<3 s) y la satisfacción del usuario.

## Instalación

```bash
pip install -r requirements.txt
# para el chatbot es necesario tener Ollama instalado y ejecutandose
```

También es posible levantar la API y la base de datos con Docker:

```bash
docker-compose up -d
```

## Entrenamiento del modelo

```bash
python main.py --train
```

## Uso de predicciones

```bash
python main.py --predict '{"age":0.05, "sex":0.02, "bmi":0.03, "bp":0.04, "s1":0.05, "s2":0.06, "s3":0.07, "s4":0.08, "s5":0.09, "s6":0.1}'
```

## Ejecutar tests

```bash
pytest tests/
```

## Levantar la API manualmente

```bash
uvicorn backend.api:app --reload
```

## Frontend y chatbot (Ollama)

```bash
streamlit run frontend/webapp.py
python chatbot/bot.py  # requiere instancia de Ollama corriendo en localhost
```
