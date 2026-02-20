FROM python:3.11-slim

# Impede que o Python gere arquivos .pyc e permite log em tempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Instala dependências do Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto para dentro do container
COPY . /app/

# Garante que o manage.py tenha permissão de execução (ajuste para Linux/Mac)
RUN chmod +x manage.py

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]