# Projet Talk Master Back

## Description

Ce projet est le backend du projet **Talk Master**.  
Il est développé en **Python** et inclut une configuration pour la base de données.  

---

## Prérequis

Assurez-vous d'avoir les outils suivants installés sur votre machine :

- Python **3.10+**
- **Docker** et **Docker Compose**
- **Git**

---

## Installation

Clonez ce dépôt :

```
git clone https://github.com/DFarau/Projet-Talk-Master-Back.git
cd Projet-Talk-Master-Back
```

Créez et activez un environnement virtuel Python :

```
python3 -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

Installez les dépendances :

```
pip install -r requirements.txt
```

## Configuration de la base de données

Assurez-vous que Docker est actif sur votre machine.

Vérifiez la configuration de la base de données dans le fichier `docker-compose.yml` :

- Par défaut, une base de données **PostgreSQL** est utilisée.
- Les variables comme `POSTGRES_USER`, `POSTGRES_PASSWORD` et `POSTGRES_DB` peuvent être modifiées selon vos besoins.

Lancez la base de données avec Docker Compose :

```
docker-compose up -d
```

Une fois la base de données lancée, appliquez les migrations pour configurer les tables nécessaires :
```
python manage.py migrate
```

# Lancer le projet

Démarrez le serveur de développement :

```
python manage.py runserver
```

Le backend sera accessible à l'adresse suivante :

http://127.0.0.1:8000/


