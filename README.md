[La version française suit.](#---------------------------------------------------------------------)

# COVID Healthcare Portal

This repository implements a healthcare portal to complement the [Government of Canada COVID Shield mobile app](https://github.com/cds-snc/covid-shield-mobile). This portal provides authenticated healthcare providers unique temporary codes which can be shared with COVID-diagnosed individuals. This code gives individuals access to upload their random IDs via the mobile app if they choose. No personal information is collected and there is no association between the codes and specific tests.

For more information on how this all works, read through the [COVID Shield Rationale](https://github.com/CovidShield/rationale).

## Setup

### Activating a virtualenv

Install [`pipenv`](https://pypi.org/project/pipenv/).

```sh
# cd into project folder
pipenv --three  # create a new virtualenv
pipenv shell    # activate virtualenv
pipenv install  # install dependencies
```

### Running the app for the first time

Make sure you have activated your virtual environment and move into the top-level `portal` folder.
Copy `./portal/.env.example` to `./portal/.env` and provide the appropriate values for your configuration.

#### 1. Database migrations

A Postgres database will need to be set up.

If a `DATABASE_URL` environment variable exists, it will set all the connection parameters at the same time. Otherwise, the database parameters will be set individually:

- `DATABASE_USERNAME`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`

We assume a database named `covid_portal` exists for local development.

To create the database schema, run `python manage.py makemigrations`.

Then, create the tables by running `python manage.py migrate`.

#### 2. Compile SCSS files to CSS

You will need to generate the `profiles/static/css/styles.css` file by compiling the SCSS files. To generate the file once, run:

```
python manage.py sass profiles/static/scss/ profiles/static/css/
```

If you are developing the app and want your styling changes applied as you make changes, you can use the `--watch` flag.

```
python manage.py sass profiles/static/scss/ profiles/static/css/ --watch
```

Note that watching the SCSS will require a new terminal window to run the development server. If you are using iTerm, you can open another tab with `Command + t` or a new pane with `Command + d`. Remember to activate your virtual environment in your new pane using `pipenv shell` and `pipenv install`.

#### 3. Create admin super user (optional)

This app allows you to use the admin (`/admin`) to manage users, although users can sign up themselves.

In order to access the `/admin` route, you will need to create a super user account to access the admin.

Run `python manage.py createsuperuser` to create a super user.

#### 4. Run development server

Then, run `python manage.py runserver` to run the app. Go to `http://127.0.0.1:8000/` to see the landing page.

### Running using Docker Compose

> [Compose](https://docs.docker.com/compose/) is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application’s services. Then, with a single command, you create and start all the services from your configuration.

You can use Docker Compose to build an application container along with a Postgres database. It will map your local files into a Docker container, spin up a PostgreSQL database, and do CSS compilation and a DB migration. The app runs on port `8000`, the database at port `5432` (u: `user`, p: `password`) and will be served at `http://0.0.0.0:8000`.

Read the step-by-step process at [Django, Docker, and PostgreSQL Tutorial](https://learndjango.com/tutorials/django-docker-and-postgresql-tutorial).

### Run

1. Spin up the app: `docker-compose up`
2. Spin down the app: `Command + c` or `docker-compose down`

### Translations

We're using the default Django translations library to add content in French and English.

Here is a short overview of adding a translated string to the application.

Add your string to a template using the `trans` tag.

```
# profiles/templates/profiles/start.html

<h1>{% trans "Generate code for Exposure Notification app" %}</h1>
```

Run `python manage.py makemessages -l fr` to update the `django.po` translations file inside of `/locale`.

```
# locale/fr/LC_MESSAGES/django.po

#: profiles/templates/profiles/start.html:7
msgid "Generate code for Exposure Notification app"
msgstr "Générer du code pour l'application de notification d'exposition"
```

Run `python manage.py compilemessages` to compile the translations so that Django knows how to use them.

For more complete documentation refer to the [Django Translation](https://docs.djangoproject.com/en/3.0/topics/i18n/translation/#translation) docs.

## ---------------------------------------------------------------------

# Portail de soins de santé COVID

Ce dépôt met en oeuvre un portail de soins de santé qui accompagne l’[application mobile COVID Shield du gouvernement du Canada](https://github.com/cds-snc/covid-shield-mobile). Ce portail fournit des codes temporaires à utilisation unique aux professionnels de la santé authentifiés, et ces codes peuvent être transmis aux personnes ayant un diagnostic de COVID-19. Le code permet aux personnes de téléverser les ID aléatoires de l’application mobile si elles acceptent. Aucune information personnelle n’est recueillie, et aucun lien n’est établi entre les codes et les tests.

Pour plus d’information sur la façon dont tout cela fonctionne, référez-vous au [raisonnement derrière COVID Shield](https://github.com/CovidShield/rationale) (en anglais).

## Configuration

### Activer un virtualenv

Installez [`pipenv`](https://pypi.org/project/pipenv/).

```sh
# cd into project folder
pipenv --three  # create a new virtualenv
pipenv shell    # activate virtualenv
pipenv install  # install dependencies
```

### Exécuter l’appli pour une première fois

Assurez-vous d’avoir activé l’environnement virtuel et déplacez-vous dans le dossier de haut niveau `portal`.
Copiez `./portal/.env.example` vers `./portal/.env` et fournissez les valeurs adéquates pour votre configuration.

#### 1. Migrations de bases de données

Une base de données Postgres devra être configurée.

Si une variable d’environnement `DATABASE_URL` existe, elle configurera tous les paramètres de connexion au même moment. Sinon, les paramètres de la base de données seront configurés individuellement :

- `DATABASE_USERNAME`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`

Nous supposons qu’une base de données nommée `covid_portal` existe pour le développement local.

Pour créer le schéma de base de données, exécutez `python manage.py makemigrations`

Ensuite, créez les tableaux en exécutant `python manage.py migrate`

#### 2. Compilation des fichiers SCSS en CSS

Vous devrez générer le fichier `profiles/static/css/styles.css` en compilant les fichiers SCSS. Pour générer le fichier une seule fois, exécutez :

```
python manage.py sass profiles/static/scss/ profiles/static/css/
```

Si vous développez l’application et que vous voulez voir vos changements de styles être appliqués au fur et à mesure que vous les faites, vous pouvez utiliser le flag `--watch`.

```
python manage.py sass profiles/static/scss/ profiles/static/css/ --watch
```

Remarquez que surveiller ainsi le SCSS nécessitera d’avoir une nouvelle fenêtre du terminal pour exécuter le serveur de développement. Si vous utilisez iTerm, vous pouvez ouvrir un nouvel onglet avec `Command + t` ou ajouter une subdivision avec `Command + d`. N’oubliez pas d’activer votre environnement virtuel dans votre nouvelle subdivision à l’aide de `pipenv shell` et `pipenv install`.

#### 3. Création d’un super utilisateur admin (facultatif)

Cette application vous permet d’utiliser l’admin (`/admin`) pour gérer les utilisateurs, même si les utilisateurs peuvent s’inscrire eux-mêmes.

Pour accéder au chemin `/admin` vous devrez créer un compte de super utilisateur.

Exécutez `python manage.py createsuperuser` pour créer un super utilisateur.

#### 4. Exécution du serveur de développement

Exécutez ensuite `python manage.py runserver` pour faire fonctionner l’application. Rendez-vous à `http://127.0.0.1:8000/` pour voir la page d’accueil.

### Exécuter avec Docker Compose

> [Compose](https://docs.docker.com/compose/) est un outil pour définir et exécuter des applications Docker multiconteneurs. Avec Compose, vous utilisez un fichier YAML pour configurer les services de votre application. Puis, avec une seule commande, vous créez et lancez tous les services à partir de votre configuration.

Vous pouvez utiliser Docker Compose pour construire un conteneur d’application parallèlement à une base de données Postgres. Il va mapper vos fichiers locaux dans un conteneur Docker, créer une base de données PostgreSQL et faire une compilation CSS et une migration de base de données. L’application s’exécute sur le port `8000`, la base de donnée sur le port `5432` (u: `user`, p: `password`) et sera desservie à l’adresse `http://0.0.0.0:8000`.

Vous pouvez les le processus étape par étape sur [Django, Docker, et PostgreSQL Tutorial](https://learndjango.com/tutorials/django-docker-and-postgresql-tutorial) (en anglais).

### Exécuter

1. Créez l’application : `docker-compose up`
2. Arrêter l’exécution de l’application : `Command + c` ou `docker-compose down`

### Traductions

Nous utilisons la bibliothèque Django par défaut pour ajouter de contenu en anglais et en français.

Voici un survol rapide de la façon d’ajouter des chaînes de caractères traduites dans l’application.

Ajoutez votre chaîne de caractères à un modèle en utilisant le tag `trans`.

```
# profiles/templates/profiles/start.html

<h1>{% trans "Generate code for Exposure Notification app" %}</h1>
```

Exécutez `python manage.py makemessages -l fr` pour mettre à jour le fichier de traductions `django.po` à l’intérieur de `/locale`.

```
# locale/fr/LC_MESSAGES/django.po

#: profiles/templates/profiles/start.html:7
msgid "Generate code for Exposure Notification app"
msgstr "Générer du code pour l'application de notification d'exposition"
```

Exécutez `python manage.py compilemessages` pour compiler les traductions afin que Django sache comment les utiliser.

Pour obtenir de la documentation plus exhaustive, veuillez vous référer à celle des [traductions Django](https://docs.djangoproject.com/en/3.0/topics/i18n/translation/#translation) (en anglais).
