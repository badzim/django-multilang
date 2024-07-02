# Utiliser une image Python officielle comme image de base
FROM python:3.12-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de l'application dans le répertoire de travail
COPY . /app

# Installer les dépendances nécessaires pour compiler les packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev

# Install gettext for message compilation
RUN apt-get update && apt-get install -y gettext

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Compile the translations
RUN python manage.py compilemessages

# Exposer le port sur lequel l'application va tourner
EXPOSE 8000

