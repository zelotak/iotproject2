FROM python:3.12-slim

# Crée un dossier de travail
WORKDIR /app

# Installe nmap et les dépendances système utiles
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        nmap gcc build-essential libffi-dev libssl-dev python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie et installe les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout ton code
COPY . .

# Expose le port pour ton app Flask
EXPOSE 5000

# Lance ton backend (à adapter si tu utilises `flask run` ou autre)
CMD ["python", "AppFlask.py"]
