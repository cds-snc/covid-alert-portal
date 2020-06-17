# healthcare-portal
Example for creating a custom user in django during a webinar. 

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

The database will need to be set up. To create the database schema, run
`python manage.py makemigrations`

Then, create the tables by running `python manage.py migrate`

This app assumes you will be using the admin (`/admin`) to manage users. Before running your app for the first time, you will need to create a super user account to access the admin. 
Run `python manage.py createsuperuser` to create a super user.

Then, run `python manage.py runserver` to run the app, and navigate to `/admin` to see the custom user model in action. 