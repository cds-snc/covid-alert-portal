# covid-healthcare-portal

Reference implementation of a healthcare portal for Canadian healthcare providers. Allows healthcare providers to generate temporary tracking codes for positively diagnosed patients.

The main thing it needs to do is user management.

Using this project as a basis: [jlooney/custom-user-example](https://github.com/jlooney/custom-user-example)

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

If a `DATABASE_URL` environment variable exists, it will set all the connection parameters at the same time. Otherwise, the database paremeters will be set individually:

- `DATABASE_USERNAME`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`

We assume a database named `covid_portal` exists for local development.

To create the database schema, run `python manage.py makemigrations`

Then, create the tables by running `python manage.py migrate`

#### 2. Compile SCSS files to CSS

You will need to generate the `profiles/static/css/styles.css` file by compiling the SCSS files. To generate the file once, run:

```
python manage.py sass profiles/assets/scss/ profiles/static/css/
```

If you are developing the app and want your styling changes applied as you make changes, you can use the `--watch` flag.

```
python manage.py sass profiles/assets/scss/ profiles/static/css/ --watch
```

Note that watching the SCSS will require a new terminal window to run the development server. If you are using iTerm, you can open another tab with `Command + t` or a new pane with `Command + d`. Remember to activate your virtual environment in your new pane using `pipenv shell` and `pipenv install`

#### 3. Create admin super user (optional)

This app allows you to use the admin (`/admin`) to manage users, although users can sign up themselves.

In order to access the `/admin` route, you will need to create a super user account to access the admin.

Run `python manage.py createsuperuser` to create a super user.

#### 4. Run development server

Then, run `python manage.py runserver` to run the app.

- Go to `/code` to see an example tracking code for a user to upload through their app
- Go to `/admin` to register new users the custom user model
- Go to `/profiles` to see the list of users
- Go to `/signup` to register a new user

### Running using Docker Compose

> [Compose](https://docs.docker.com/compose/) is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application’s services. Then, with a single command, you create and start all the services from your configuration.

You can use Docker Compose to build an application container along with a Postgres database. It will map your local files into a Docker container, spin up a PostgreSQL database, and do CSS compliation and a DB migration. The app runs on port `8000`, the database at port `5432` (u: `user`, p: `password`) and will be served at `http://0.0.0.0:8000`.

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
