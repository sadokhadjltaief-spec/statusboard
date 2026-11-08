FROM python:3.12-slim

# Empêche Python de générer des fichiers .pyc et active les logs en temps réel
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# On installe d'abord les dépendances (optimise le cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie le code
COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]