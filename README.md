# CoinCanvas

## Author: James Brooks

## Description

Coin Canvas is a simple and easy to use website that allows users to sign in and view a chart representing the price history of a given Stock or Crypto Currency that remembers the user's desired charts so long as they were signed in when they viewed them.

It is designed to be lightweight and with as few extraneous additions as possible as well as providing the data in an easy to understand format.

The project is primarily a remake and expansion upon a project I previously worked on with a group during my education called Chartify, the link to the GitHub Repo of the original project can be found here: [Link](https://github.com/open-bracket-space-close-bracket/chartify)

## Links and Resources

- [Front-End Application Link](https://coin-canvas-eight.vercel.app)
- [API Resource - Polygon.io](https://polygon.io)

- ENV Requirements
  - Database
    - POSTGRES_URL2 - The url for the database you plan to use. It is intended to be used with a PostgreSQL database and I do not know if it will work with others. For PostgreSQL, the format must be postgresql not postgres due to SQLALchemy not supporting the latter.
  - Auth0
    - AUHT0_CLIENT_ID - The client id for your Auth0 Integration
    - AUTH0_CLIENT_SECRET - The client secret for your Auth0 Integration
    - AUTH0_DOMAIN -  The domain for your Auth0 Integration
  - API
    - POLYGON_API_KEY - Your API key for Polygon.io.
  - App Specific
    - APP_SECRET_KEY - The secret key for your app to act as authorization for various route requests. To generate the secret key, run the command `openssl rand -hex 32` in your terminal and copy/paste the result as the env value.
    - APP_URL -  The root url for the application. If running locally, this is likely to be 127.0.0.1:5000. If deployed, it will be the root url for the deployed website.
    - TEST_USER - The email for a user in the database that is used for pytests on the production database.
- To run on your local machine, you use the command `flask run`.
  - However, when you first set up the application, you need to run the migrations to set up the database properly with Flask-Migrate. There are 3 command you run in sequence.
    - `flask db init` to create the migration directory
    - `flask db migrate` to let Alembic detect changes to the model
    - `flask db upgrade` to apply the changes.
  - You will need to run the migrate and upgrade commands every time you change the database model in the future.

## Tests

- Test Command (TODO)
- Number of Tests (TODO)
- Test Coverage (TODO)
