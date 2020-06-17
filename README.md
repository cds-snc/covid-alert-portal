# healthcare-portal

Reference implementation of a healthcare portal for Canadian healthcare providers. Allows healthcare providers to generate temporary tracking codes for positively diagnosed patients.

The main thing it needs to do is user management stuff.

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

Make sure you have activated your virtual environment.

The database will need to be set up. To create the database schema, run
`python manage.py makemigrations`

Then, create the tables by running `python manage.py migrate`

This app allows you to use the admin (`/admin`) to manage users, although users can sign up themselves.

In order to access the `/admin` route, you will need to create a super user account to access the admin. 

Run `python manage.py createsuperuser` to create a super user.

Then, run `python manage.py runserver` to run the app.

- Navigate to `/admin` to see the custom user model. 
- Navigate to `/signup` to create a non-admin user account