# Documentation Chatbot Project

Ce projet est une application Django qui intègre un chatbot utilisant OpenAI pour répondre aux questions des utilisateurs basées sur la documentation. Le chatbot peut détecter la langue du contexte et répondre dans la langue préférée de l'utilisateur.

## Prérequis

- Python 3.10+
- OpenAI API
- Docker (optionnel)
- gettext


## Utilisation avec Docker Compose

Assurez-vous que Docker et Docker Compose sont installés sur votre machine.

### 1. Configurer les clés API

Créez un fichier `.env` à 'la racine du projet' et ajoutez votre clé API OpenAI :

```sh
OPENAI_API_KEY=<votre-cle-api-openai>
```

### 2. Exécuter Docker Compose

```sh
docker-compose up --build
```

Cela construira et démarrera les conteneurs définis dans `/docker-compose.yml`.

### 3. Tester l'application
Utilisez votre navigateur préféré et naviguez vers http://localhost:8000.

## Installation Sans Dcoker

### 1. Créer et activer un environnement virtuel

```sh
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 2. Installer les dépendances

```sh
pip install -r requirements.txt
```

### 3. Configurer les clés API
```sh
export OPENAI_API_KEY=<votre-cle-api-openai>
```

### 4. Effectuer les migrations et démarrer le serveur

```sh
python manage.py makemigrations
python manage.py migrate
python django-admin compilemessages
python manage.py runserver
```