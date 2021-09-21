[La version française suit.](#portail-de-soins-de-santé-covid)

# COVID Alert Portal

The COVID Alert Portal provides authenticated healthcare providers unique temporary codes which can be shared with COVID-diagnosed individuals. The code enables individuals to upload their random IDs via the mobile app if they choose. No personal information is collected by the app and there is no association between the codes and specific tests. The Portal complements the [Government of Canada COVID Alert app](https://github.com/cds-snc/covid-alert-app).

A healthcare portal is one of the three pieces of the [COVID Shield](https://www.covidshield.app/) open-source reference implementation built by Shopify volunteers. For a high-level view on how the components work together, read through the [COVID Shield Rationale](https://github.com/CovidShield/rationale).

## COVID Alert Outbreaks and Business Registration Site

The COVID Alert Business Registration Site is part of the Outbreaks feature of COVID Alert Portal. Outbreaks is a new feature developed to help public health and businesses in their contact tracing efforts. Business owners can register and print a poster that includes a QR Code. Visitors to their location that have COVID Alert installed on their device can scan the QR Code to record their visit. Subsequently, if public health authorites identify an Outbreak at that location, they can send alerts to people who may have been exposed through COVID Alert.

This project includes the code for both the COVID Alert Portal and the COVID Alert Business Registration Site, but the two websites are deployed separately, and this project can only be run in one mode or the other. 

The mode of the project is determined by an [Environment variable](#environment-variables):

- `APP_SWITCH=QRCODE` will run the registration site
- `APP_SWITCH=PORTAL` will run the portal

## Table of contents

- [Running the project](#running-the-project)
  - [Environment variables](#environment-variables)
- [Local development](#local-development)
  - [External dependencies](#external-dependencies)
  - [Activating a virtualenv](#activating-a-virtualenv)
  - [Database](#database)
    - [Database migrations](#database-migrations)
  - [Compile CSS](#compile-css)
  - [Create admin superuser](#create-admin-super-user-optional)
  - [Run development server](#run-development-server)
- [Running using Docker Compose](#running-using-docker-compose)
- [Translations](#translations)
- [Development workflow](#development-workflow)
  - [Feature development](#feature-development)
  - [Application versioning](#application-versioning)
  - [Automated tests](#automated-tests)

## Running the project

The COVID Alert Portal is a Django application: it can be run as a python process or using `docker-compose`.

- [Running the COVID Alert Portal locally](#local-development) as a python process requires [python3](https://www.python.org/downloads/) and a PostgreSQL database.
- [Using `docker-compose`](#running-using-docker-compose), you’ll need [Docker](https://www.docker.com/get-started) installed.

### Environment variables

Environment variables are used to control app settings, and configuration for utilities and third-party services. Defaults are `''` or `None` unless otherwise specified.

Before running the project, you will need to copy `./portal/.env.example` to `./portal/.env` and provide the appropriate values for your configuration.

<details>
<summary>Detailed explanation of each environment variable</summary>
<div>

#### App settings

- `DJANGO_ENV` (default: `development`): Turns on [`DEBUG`](https://docs.djangoproject.com/en/3.0/ref/settings/#debug) mode, as well as doesn't require HTTPS to run. For local development, leave this as `development`.

- `DJANGO_SECRET_KEY`: The `SECRET_KEY` in Django is used to provide cryptographic signing, and should be set to a unique, unpredictable value. Django won't start unless this is set. [Read the docs here](https://docs.djangoproject.com/en/3.0/ref/settings/#secret-key).

- `DJANGO_ALLOWED_HOSTS`: A list of strings representing the host/domain names that this Django site can serve. Only needs to be set in prod. [Read the docs here](https://docs.djangoproject.com/en/3.0/ref/settings/#allowed-hosts).

- `SU_DEFAULT_PASSWORD`: Setting to trigger the creation of a default superuser the first time the app is provisioned. If this variable exists, a default superuser will be created at `admin@cds-snc.ca` with this password.

- `QRCODE_SIGNATURE_PRIVATE_KEY`: Private key for signing QR Code payloads. Should be a Base64 encoded key generated with the [PyNaCl encryption library](https://pynacl.readthedocs.io/)

- `APP_SWITCH`: Should be set to `QRCODE` or nothing. This determines whether the app will run in "Registration site" mode, or "Portal" mode.

##### database configuration

- `DATABASE_URL`: A string containing the database scheme, host, username, password, and port. The `DATABASE_URL` is parsed by [`dj-django-url`](https://pypi.org/project/dj-database-url/).

#### CovidAlert API settings

- `API_ENDPOINT`: The API endpoint that returns one-time usage codes. If not set, the one-time codes will read as `0000 0000`.

- `API_AUTHORIZATION`: The credentials required to authenticate with the one-time code API. Otherwise the request will return a `401` Forbidden response.

#### OTP (2-factor) configuration

We use Notify and django-otp to send 2FA auth codes via SMS.

- `OTP_NOTIFY_ENDPOINT`: Changes the default Notify endpoint used.

- `OTP_NOTIFY_API_KEY`: The API key used to call Notify

- `OTP_NOTIFY_NO_DELIVERY`: Used in tests, prints the token in the console instead of calling Notify.

- `OTP_NOTIFY_TOKEN_VALIDITY`: Time in seconds before the token expires

[Read the docs here](https://django-otp-notify.readthedocs.io/en/latest/)

#### Contact form and Freshdesk

The contact form sends any inquiry to Freshdesk.

- `FRESHDESK_API_KEY`: Your user API key generated in Freshdesk.

- `FRESHDESK_API_ENDPOINT`: Your Freshdesk domain with `/api/v2/` at the end.

- `FRESHDESK_PRODUCT_ID`: If you use more than one product, use this variable to specify where the feedback should go to.

##### Email configuration

- We use [GC Notify](https://notification.canada.ca/) for sending all user-facing emails and text messages.

#### New Relic configuration

We use New Relic to monitor for server side errors and application performance in production and staging. We do not leverage New Relic client (browser side) metric reporting.

- `NEW_RELIC_APP_NAME`: The app name set up in New Relic.

- `NEW_RELIC_LICENSE_KEY`: Credentials needed to authenticate with New Relic.

</div>
</details>

<strong>[Example `.env` file](https://github.com/cds-snc/covid-healthcare-portal/blob/main/portal/.env.example)</strong>

## Local development

This section describes how to get the project running on your local device. You can alternatively [run using docker-compose](#running-using-docker-compose) which will include all required dependencies and services and may be a simpler setup depending on your preference and experience.

### External dependencies

If you are running the app using Docker Compose, this dependency is already included. If you are running in a local virtual environment, you'll need to install cairo for PDF poster generation.

Using Homebrew on MacOS: 

```
brew install cairo
```

### Activating a virtualenv

Install [`pipenv`](https://pypi.org/project/pipenv/).

```sh
# cd into project folder
pipenv --three       # create a new virtualenv
pipenv shell         # activate virtualenv
pipenv install --dev # install dev dependencies
```

### Database

You will need to have a PostgreSQL database running. You can install one using Homebrew on MacOS: 

```
brew install postgresql
```

NOTE: Earlier versions of this project would default to using a SQLite database if none is configured. Some features have been introduced in the Outbreaks feature that depend on features of PostgreSQL, so SQLite is no longer recommended.

Ensure that you have configured the `DATABASE_URL` environment variable according to your PostgreSQL config, using the following format:

`postgres://USER:PASSWORD@HOST:PORT/NAME`

#### Database migrations

Migrate the database by running:

```
python manage.py migrate
```

When creating or modifying existing models, you will need to generate migrations to keep your database in sync:

```
python manage.py makemigrations
```

For more information, see [Django Migrations](https://docs.djangoproject.com/en/3.2/topics/migrations/).

### Compile CSS

To compile the SCSS files to CSS once:

```
pipenv run css
```

If you are developing the app and want your styling changes applied as you make changes, you can use the csswatch command:

```
pipenv run csswatch
```

### Create admin super user (optional)

This app allows you to use the Django admininstration panel (`/admin`) to manage users.

In order to access the `/admin` route, you will need to create a super user account to access the admin.

Run `python manage.py createsuperuser` to create a super user.

### Run development server

Then, run `python manage.py runserver` to run the app. Go to `http://127.0.0.1:8000/` to see the login page.

## Running using Docker Compose

> [Compose](https://docs.docker.com/compose/) is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application’s services. Then, with a single command, you create and start all the services from your configuration.

You can use Docker Compose to build an application container along with a Postgres database. It will map your local files into a Docker container, spin up a PostgreSQL database, and do CSS compilation and a DB migration. The app runs on port `8000`, the database at port `5432` (u: `user`, p: `password`) and will be served at `http://0.0.0.0:8000`.

Read the step-by-step process at [Django, Docker, and PostgreSQL Tutorial](https://learndjango.com/tutorials/django-docker-and-postgresql-tutorial).

### Run

1. Spin up the app: `docker-compose up`
2. Spin down the app: `Command + c` or `docker-compose down`

## Translations

We're using the default [Django translation](https://docs.djangoproject.com/en/3.2/topics/i18n/translation/) library to add content in French and English.

When you have updated or added a new localized string, for example in a template file:

```
# profiles/templates/profiles/start.html

<h1>{% trans "Generate code for Exposure Notification app" %}</h1>
```

You will need to run the following command which will scan the the application for localized strings and add them to the locale files:

```
python manage.py makemessages -l fr --add-location=file --no-wrap
```

This command will collect all localized strings to the `locale/django.po` file. For example:

```
# locale/fr/LC_MESSAGES/django.po

#: profiles/templates/profiles/start.html:7
msgid "Generate code for Exposure Notification app"
msgstr "Générer du code pour l'application de notification d'exposition"
```

Once the string has been translated in the .po file, you will need to compile the translations to the `django.mo` file by running the following command:

```
python manage.py compilemessages
```

For more complete documentation refer to the [Django Translation](https://docs.djangoproject.com/en/3.0/topics/i18n/translation/#translation) docs.

## Development workflow

### Feature development

Feature development on the Portal follows a [trunk-based development](https://trunkbaseddevelopment.com/) workflow. The `main` branch has the most up-to-date code and is always production-ready. When starting a new feature (or a bugfix, etc.), a new branch is created from the tip of the `main` branch. Once the work is complete, the feature is merged back into `main` via a Pull Request (PR). PRs must pass a series of [automated tests](https://github.com/cds-snc/covid-alert-portal#automated-tests) (unit tests, linting, etc), as well as a manual review by another developer. After the automated tests pass and the PR is approved, the code is merged into `main` and the feature branch is deleted. The `main` branch is protected from direct pushes or force pushes — pull requests are mandatory.

### Application versioning

We keep the version number in a root-level [`VERSION` file](https://github.com/cds-snc/covid-alert-portal/blob/main/VERSION) and the list of changes between versions in the root [`CHANGELOG.md` file](https://github.com/cds-snc/covid-alert-portal/blob/main/CHANGELOG.md). We follow [semantic versioning conventions](https://semver.org/) and for the Changelog file we follow the format suggested by [keepachangelog.com](https://keepachangelog.com/en/1.0.0/).

Not all PRs will update the app version — in fact, most of them don’t. PRs with new features or bug fixes require an update to the Changelog file, under “Unreleased”. When the version is next incremented, all of the unreleased changes are included as part of the version bump. It’s okay if something doesn’t make it into the Changelog when it is merged — `CHANGELOG.md` is a file like any other and can be corrected retroactively.

Note that releasing a change to production **requires** incrementing the `VERSION` file. The Changelog is kept up-to-date by convention, but it is not formally required to be in sync with the version in the VERSION file.

### Automated tests

We are using [GitHub Actions](https://github.com/features/actions) as our CI platform: it runs our automated tests for us and automates our deployments.

Our automated tests include:

- `pipenv run test`: Runs our suite of unit tests (on CI we run them in Python versions 3.6, 3.7, 3.8)
- `pipenv run format --check`: uses the `black` Python formatter to ensure consistency of our code
- `pipenv run lint`: uses `flake8` to ensure Python style guide compliance
- Snyk (SaaS): checks for vulnerable dependencies
- LGTM (SaaS): checks for code smells and insecure coding practices
- `terraform plan`: if the terraform config has been modified, `terraform plan` will return a diff of changes between the current infrastructure and the files in the PR.
- `terraform security-scan`: will flag any unsafe configuration changes

We also have an automated test for code coverage, which will fail if code coverage falls below 80%. We are using the [`coverage`](https://coverage.readthedocs.io/en/coverage-5.3/) library, as recommended by the Django docs. Configuration for `coverage` is found in [`pyproject.toml`](https://github.com/cds-snc/covid-alert-portal/blob/main/pyproject.toml).

- `pipenv run coverage_test`: run the unit tests to generate the report
- `pipenv run coverage_report`: display the report

---

[La version française suit.](#portail-de-soins-de-santé-covid)

# Portail Alerte COVID

Le portail Alerte COVID produit des codes uniques temporaires que les fournisseurs de soins de santé peuvent transmettre aux personnes ayant reçu un diagnostic positif de COVID-19. Le code permet à ces personnes de téléverser leurs identifiants anonymes à l’aide de l’application mobile. Aucune information personnelle n’est recueillie, et aucun lien n’est établi entre les codes et les tests Le portail complète l’application [Alerte COVID du gouvernement du Canada](https://github.com/cds-snc/covid-alert-app).

Le portail des soins de santé est l’un des trois éléments du référentiel source ouvert [COVID Shield](https://www.covidshield.app/) développé par des bénévoles de Shopify. Pour une vue d’ensemble des interactions entre les composantes, lisez la [justification de COVID Shield](https://github.com/CovidShield/rationale).

## Fonction éclosions d’Alerte COVID et site d’inscription des entreprises

Le site d’inscription des entreprises d’Alerte COVID fait partie de la fonction éclosions du portail Alerte COVID. La nouvelle fonction éclosions a été développée pour aider les autorités de santé publique et les entreprises dans leurs efforts de recherche des contacts. Les propriétaires d’entreprise peuvent s’inscrire et imprimer une affiche qui comprend un code QR. Les gens qui ont installé Alerte COVID sur leur appareil et qui visitent un de ces lieux peuvent scanner le code QR pour enregistrer leur visite. Par la suite, si les autorités de santé publique déterminent qu’une éclosion s’est produite dans ce lieu, elles peuvent envoyer des alertes (à l’aide d’Alerte COVID) aux personnes qui pourraient avoir été exposées.

Ce projet comprend le code du portail Alerte COVID et du site d’inscription des entreprises d’Alerte COVID, mais les deux sites Web sont déployés séparément et ce projet ne peut être exécuté que dans un mode ou dans l’autre. 

Le mode du projet est déterminé par une [variable d’environnement](#environment-variables) :

- `APP_SWITCH=QRCODE` exécute le site d’inscription
- `APP_SWITCH=PORTAL` exécute le portail

## Table des matières

- [Exécution du projet](#running-the-project)
  - [Variables d’environnement](#environment-variables)
- [Développement local](#local-development)
  - [Dépendances externes](#external-dependencies)
  - [Activer un virtualenv](#activating-a-virtualenv)
  - [Base de données](#database)
    - [Migrations de bases de données](#database-migrations)
  - [Compiler le code CSS](#compile-css)
  - [Créer un superutilisateur administrateur](#create-admin-super-user-optional)
  - [Exécuter le serveur de développement](#run-development-server)
- [Exécuter l’application à l’aide de docker-compose](#running-using-docker-compose)
- [Traductions](#translations)
- [Flux de travail de développement](#development-workflow)
  - [Développement de fonctionnalités](#feature-development)
  - [Gestion des versions de l’application](#application-versioning)
  - [Tests automatisés](#automated-tests)

## Exécution du projet

Le portail Alerte COVID est une application Django : elle peut être exécutée comme processus python ou à l’aide de `docker-compose`.

- [L’exécution du portail d’alerte COVID localement](#local-development) en tant que processus python nécessite [python3](https://www.python.org/downloads/) et une base de données PostgreSQL.
- [Pour utiliser `docker-compose`](#running-using-docker-compose), il faut d’abord installer [Docker](https://www.docker.com/get-started).

### Variables d’environnement

Les variables d’environnement sont utilisées pour contrôler les paramètres de l’application et la configuration d’utilitaires et de services tiers. Les valeurs par défaut sont `''` ou `None`, sauf indication contraire.

Avant d’exécuter le projet, vous devrez copier `./portal/.env.example` dans `./portal/.env` et fournir les valeurs appropriées pour votre configuration.

<details>
<summary>Explication détaillée de chaque variable d’environnement</summary>
<div>

#### Paramètres de l’application 
- `DJANGO_ENV` (par défaut : `development`) : Active le mode [`DEBUG`](https://docs.djangoproject.com/en/3.0/ref/settings/#debug) et ne nécessite pas HTTPS pour s’exécuter. Pour le développement local, laissez ce paramètre à `development`. 
- `DJANGO_SECRET_KEY` : `SECRET_KEY` dans Django sert à fournir une signature cryptographique. Assurez-vous de définir une valeur unique et aléatoire.  Django ne démarrera pas si cette valeur n’a pas été définie. [Cliquer ici pour lire la documentation] (https://docs.djangoproject.com/en/3.0/ref/settings/#secret-key). 
- `DJANGO_ALLOWED_HOSTS` : Liste de chaînes représentant les noms d’hôte/de domaine que le site Django peut prendre en charge. Doit seulement être réglé dans l’environnement de production. [Cliquer ici pour lire la documentation] (https://docs.djangoproject.com/en/3.0/ref/settings/#allowed-hosts). 
- `SU_DEFAULT_PASSWORD` : Paramètre qui déclenche la création d’un superutilisateur par défaut la première fois que l’application est mise en service. Si cette variable existe, un superutilisateur par défaut sera créé avec l’identifiant 'admin@cds-snc.ca' et ce mot de passe. 
- `QRCODE_SIGNATURE_PRIVATE_KEY` : Clé privée pour signer les données à transmettre pour les codes QR. Il doit s’agir d’une clé chiffrée en Base64 générée selon la base de données de la [bibliothèque de chiffrement PyNaCl](https://pynacl.readthedocs.io/) 
- `APP_SWITCH` : Doit être réglé à `QRCODE` ou rien. Détermine si l’application s’exécute en mode « Site d’inscription » ou en mode « Portail ». 

##### Configuration de la base de données 
- `DATABASE_URL` : Chaîne contenant le schéma de base de données, l’hôte, le nom d’utilisateur, le mot de passe et le port. L’URL de base donnée (`DATABASE_URL`) est analysée par [`dj-django-url`](https://pypi.org/project/dj-database-url/). 

#### Paramètres API d’Alerte COVID 
- `API_ENDPOINT` : Le point de terminaison de l’API qui renvoie des clés à usage unique. Si elles ne sont pas définies, les clés à usage unique affichent `0000 0000`. 
- `API_AUTHORIZATION` : Les identifiants requis pour s’authentifier auprès de l’API des clés à usage unique. Sinon, la demande produira une réponse `401` interdite. 

#### Configuration de mot de passe à usage unique (2 facteurs) 

Nous utilisons GC Notification et django-otp pour envoyer des codes d’authentification 2FA par SMS. 
- `OTP_NOTIFY_ENDPOINT` : Modifie le point de terminaison GC Notification par défaut utilisé. 
- `OTP_NOTIFY_API_KEY` : La clé API utilisée pour appeler GC Notification - 
- `OTP_NOTIFY_NO_DELIVERY`: Utilisé dans les tests, inscrit le jeton dans la console plutôt que d’appeler GC Notification. 
- `OTP_NOTIFY_TOKEN_VALIDITY` : Temps en secondes avant l’expiration du jeton [Cliquer ici pour lire la documentation](https://django-otp-notify.readthedocs.io/en/latest/) 

#### Formulaire de contact et Freshdesk 

Le formulaire de contact envoie toute demande à Freshdesk. 
- `FRESHDESK_API_KEY` : Votre clé API utilisateur générée dans Freshdesk. 
- `FRESHDESK_API_ENDPOINT` : Votre domaine Freshdesk se terminant par `/api/v2/`. 
- `FRESHDESK_PRODUCT_ID` : Si vous utilisez plusieurs produits, utilisez cette variable pour préciser où les commentaires doivent être acheminés. 

##### Configuration des courriels 
- Nous utilisons [GC Notification] (https://notification.canada.ca/) pour envoyer les courriels et messages textes destinés aux utilisateurs. 

#### Configuration de New Relic 
Nous utilisons New Relic pour surveiller les erreurs côté serveur et la performance de l’application en environnement de production et de préproduction. Nous n’utilisons pas les rapports de mesures du client New Relic (côté navigateur). 
- `NEW_RELIC_APP_NAME` : Nom de l’application configurée dans New Relic. 
- `NEW_RELIC_LICENSE_KEY` : Informations d’identification nécessaires pour s’authentifier auprès de New Relic.

</div>
</details>

<strong>[Exemple de fichier `.env` ](https://github.com/cds-snc/covid-healthcare-portal/blob/main/portal/.env.example)</strong>

## Développement local

Cette section décrit comment exécuter le projet sur votre appareil local. Vous pouvez également [exécuter l’application à l’aide de docker-compose](#running-using-docker-compose) qui comprend toutes les dépendances et tous les services requis. Cette configuration peut être plus simple, selon vos préférences et votre expérience.

### Dépendances externes

Si vous exécutez l’application à l’aide de docker-compose, cette dépendance est déjà comprise. Si toutefois, vous exécutez l’application dans un environnement virtuel local, vous devez installer cairo pour générer les affiches PDF.

Utiliser Homebrew sur MacOS : 

``` brew install cairo ```

### Activer un virtualenv

Installez [`pipenv`](https://pypi.org/project/pipenv/).

```sh
# changez de répertoire (cd) pour accéder au répertoire de projet
pipenv --three # créez un nouveau virtualenv 
pipenv shell # activez le virtualenv 
pipenv install --dev # installez les dépendances dev
```

### Base de données

Vous devez exécuter une base de données PostgreSQL. Vous pouvez en installer une en utilisant Homebrew sur MacOS : 

``` brew install postgresql ```

NOTE : Les versions antérieures de ce projet utilisaient une base de données SQLite par défaut si aucune base de données n’était configurée. Certaines fonctionnalités comprises dans la fonction éclosions dépendent des fonctionnalités de PostgreSQL. Les bases de données SQLite ne sont donc plus recommandées.

Assurez-vous d’avoir configuré la variable d’environnement `DATABASE_URL` en fonction de votre configuration PostgreSQL, en utilisant le format suivant :

`postgres://USER:PASSWORD@HOST:PORT/NAME`

#### Migrations de bases de données

Migrez la base de données en exécutant :

``` python manage.py migrate ```

Lors de la création ou de la modification de modèles existants, vous devrez générer des migrations pour synchroniser votre base de données :

``` python manage.py makemigrations ```

Pour en savoir plus, consultez ce document d’aide sur les [migrations Django](https://docs.djangoproject.com/en/3.2/topics/migrations/) (en anglais).

### Compiler le code CSS

Pour compiler les fichiers SCSS en CSS une fois :

``` pipenv run css ```

Si vous développez l’application et souhaitez que vos modifications de style soient appliquées en effectuant des modifications, vous pouvez utiliser la commande csswatch :

``` pipenv run csswatch ```

### Créer un super utilisateur administrateur (facultatif)

Cette application vous permet d’utiliser le panneau d’administration Django (`/admin`) pour gérer les utilisateurs.

Pour accéder au chemin d’accès `/admin`, vous devez créer un compte super utilisateur.

Exécutez `python manage.py createsuperuser` pour créer un super utilisateur.

### Exécuter le serveur de développement

Exécutez ensuite `python manage.py runserver` pour lancer l’application. Accédez à `http://127.0.0.1:8000/` pour afficher la page d’ouverture de session.

## Exécuter l’application à l’aide de docker-compose

> [Compose](https://docs.docker.com/compose/) est un outil permettant de définir et d’exécuter des applications Docker multiconteneurs. Avec Compose, un fichier YAML est utilisé pour configurer les services de votre application. Puis, avec une seule commande, tous les services sont créés et exécutés à partir de votre configuration.

Vous pouvez utiliser Docker Compose pour créer un conteneur d’applications avec une base de données Postgres. Docker Compose établira un lien entre vos fichiers locaux et un conteneur Docker; créera une base de données PostgreSQL, et effectuera une compilation CSS et une migration de base de données. L’application s’exécute sur le port `8000`, la base de données sur le port `5432` (u : `utilisateur`, p : `mot de passe`), et est traitée à l’adresse http://0.0.0.0:8000.

Lisez le processus étape par étape dans le [tutoriel Django, Docker et PostgreSQL](https://learndjango.com/tutorials/django-docker-and-postgresql-tutorial) (en anglais).

### Exécuter l’application

1. Lancez l’application : `docker-compose up`
2. Arrêtez l’application : `Command + c` ou `docker-compose down`

## Traductions

Nous utilisons la [bibliothèque de traduction par défaut de Django](https://docs.djangoproject.com/en/3.2/topics/i18n/translation/) pour ajouter du contenu en français et en anglais.

Lorsque vous mettez à jour ou ajoutez une nouvelle chaîne localisée, par exemple dans un fichier modèle :

```
# profiles/templates/profiles/start.html

<h1>{% trans "Generate code for Exposure Notification app" %}</h1>
```

Vous devez exécuter la commande suivante pour repérer les chaînes localisées et les ajouter aux fichiers de paramètres régionaux :

``` python manage.py makemessages -l fr --add-location=file --no-wrap ```

Cette commande collectera toutes les chaînes localisées dans le fichier `locale/django.po`. Par exemple :

```
# locale/fr/LC\_MESSAGES/django.po

#: profiles/templates/profiles/start.html:7 msgid "Generate code for Exposure Notification app" msgstr "Générer du code pour l’application de notification d’exposition"
```
Une fois la chaîne traduite dans le fichier .po, vous devez compiler les traductions dans le fichier `django.mo` en exécutant la commande suivante :

``` python manage.py compilemessages ```

Pour plus de détails, consultez la documentation de [Django sur la traduction](https://docs.djangoproject.com/en/3.0/topics/i18n/translation/#translation) (en anglais).

## Flux de travail de développement

### Développement de fonctionnalités

Le développement des fonctionnalités sur le portail suit un flux de travail de [développement basé sur un tronc commun](https://trunkbaseddevelopment.com/) (en anglais). La branche `main` contient le code le plus à jour et est toujours prête pour la production. Lors de la création d’une nouvelle fonctionnalité (ou d’un correctif, etc.), une nouvelle branche est créée à partir de la pointe de la branche `main`. Une fois le travail terminé, la fonctionnalité est fusionnée dans la branche `main` au moyen d’une demande de tirage (<i>pull request</i>). Les demandes de tirage doivent subir une série de [tests automatisés](https://github.com/cds-snc/covid-alert-portal#automated-tests) (tests unitaires, analyse statique, etc.), ainsi qu’une révision manuelle par un autre développeur. Une fois les tests automatisés terminés et la demande de tirage approuvée, le code est fusionné dans la branche `main` et la branche de fonctionnalité est supprimée. La branche `main` est protégée contre le fusionnement direct ou forcé — les demandes de tirage sont obligatoires.

### Gestion des versions de l’application

Nous conservons le numéro de version dans un [fichier racine `VERSION`](https://github.com/cds-snc/covid-alert-portal/blob/main/VERSION) et le journal des modifications dans le [fichier racine `CHANGELOG.md`](https://github.com/cds-snc/covid-alert-portal/blob/main/CHANGELOG.md). Nous suivons les [conventions de la gestion sémantique des versions](https://semver.org/) pour l’application et le fichier Changelog suit le format suggéré par [keepachangelog.com](https://keepachangelog.com/en/1.0.0/).

Les demandes de tirage ne mettent pas forcément à jour la version de l’application — en fait, la plupart d’entre eux ne le font pas. Les demandes de tirage avec de nouvelles fonctionnalités ou des correctifs nécessitent une mise à jour du fichier Changelog, sous « Unreleased ». Lors de la publication d’une nouvelle version, toutes les modifications non publiées sont incluses. Ne vous en faites pas si quelque chose ne figure pas dans le journal des modifications lorsqu’une branche est fusionnée - `CHANGELOG.md` est un fichier tout à fait normal et peut être corrigé rétroactivement.

Notez que la publication d’une modification à l’environnement de production **exige** une nouvelle version du fichier `VERSION`. Le journal des modifications est tenu à jour par convention, mais ne doit pas forcément être synchronisé avec la version du fichier VERSION.

### Tests automatisés

Nous utilisons [GitHub Actions](https://github.com/features/actions) comme plateforme d’intégration continue : elle nous permet d’exécuter nos tests automatisés et d’automatiser nos déploiements.

Nos tests automatisés comprennent :

- `pipenv run test` : Exécute notre suite de tests unitaires (pour l’intégration continue, nous les exécutons dans les versions Python 3.6, 3.7, 3.8)
- `pipenv run format --check` : fait appel à l’outil de formatage Python `black` pour assurer l’uniformité de notre code
- `pipenv run lint` : fait appel à `flake8` pour assurer la conformité au guide de style Python
- Snyk (SaaS) : repère les dépendances vulnérables
- LGTM (SaaS) : repère les symptômes de code (<i>code smells</i>) et les pratiques de codage non sécurisées
- `terraform plan` : si la configuration terraform a été modifiée, `terraform plan` affichera les changements entre l’infrastructure actuelle et les fichiers dans la demande de tirage.
- `terraform security-scan` : signalera tout changement de configuration dangereux

Nous avons également un test automatisé pour la couverture du code, qui échoue si la couverture du code est inférieure à 80 %. Nous utilisons la bibliothèque [`coverage`](https://coverage.readthedocs.io/en/coverage-5.3/), selon les recommandations dans la documentation de Django. La configuration de `coverage` se trouve dans [`pyproject.toml`](https://github.com/cds-snc/covid-alert-portal/blob/main/pyproject.toml).

- `pipenv run coverage_test` : lance les tests unitaires pour générer le rapport
- `pipenv run coverage_report` : affiche le rapport

---