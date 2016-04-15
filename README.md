# happy-commas
A webservice for managing csv files.

## Installation
```
$ git clone https://github.com/dianvaltodorov/happy-commas.git
$ cd happy-commas
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ ./db_create
$ ./run.py # runs in debug
```
## Configuration:
The config.py file holds all configuration constants for setting up the project. It is highly advisable to change the `SECRET_KEY` into something hard to guess.

* `SECRET_KEY` - security secret key
* `SQLALCHEMY_DATABASE_URI` - path to the database
* `SQLALCHEMY_MIGRATE_REPO` - path to the repository, holding historical information about db migrations
* `MAX_CONTENT_LENGTH` - the maximum allowed size of files for import. Default value is set to 64MB.
* `ALLOWED_EXTENSIONS` - a set of allowed filename extensions for upload. Only ".csv" by default,
* `FILE_CREATION_FOLDER` - path to folder for creation of the exported csv file.

## Running the service:
There are two modes of running the service:
* `$ ./run.py`  - run in **DEBUG** mode
* `$ ./runp.py` - run in **PRODUCTION** mode

## Description:
A webservice for managing data in the format **(user_id, key, value)**. Each user
has a number of key­-value pairs associated with him by his user_id. There is uniqueness
by the pair **(user_id, key)**. You can’t have the same key twice for a given user.

**Example data:**

| user_id            | key                 | value               |
| :----------------- | :-----------------  | :-----------------  |
| 1                  | name                | Alice               |
| 1                  | age                 | 18                  |
| 2                  | name                | Bob                 |
| 3                  | email               | foo@bar.com         |
| 3                  | name                | John                |

**GET /export**
* Description:
  - Exports the data for the specified user_ids in CSV format.
* Parameters:
  - user_ids ​- comma separated string containing user IDs to export data for
  - keys - comma­ separated string containing keys to export
* Example:
  - Request: ​`GET /export/?user_ids=1,2&attributes=name`
  - Response:
    - OK 200 and a CSV file with the following contents:
```
user_id,key,value
1,name,Alice
2,name,Bob
3,name,John
```

    - Error Bad Request 400 on failure

**POST /import**
* Description:
  - Imports data from the uploaded CSV file. The data in the underlying storage
  is updated with the data in the CSV file.
  - Important: if a value for a key does not exist, it is added. If it exists, the
  value is updated.
* Example:
  - Upload a CSV file with the following contents
```
user_id,key,value
2,age,21
1,age,19
```
  - HTTP Response:
    - Succes, 200 OK response on success.
    - Error, 400 Bad Request reponse on failure for example wrong params
    - Error, 413 Request entity too large when imported file is too large
  - Side effect:
    - Data in the underlying storage is updated. If we have the same Example data ​
      as above, the updated data should look like this:

| user_id            | key                 | value               |
| :----------------- | :-----------------  | :-----------------  |
| 1                  | name                | Alice               |
| 1                  | age                 | 19                  |
| 2                  | name                | Bob                 |
| 2                  | age                 | 21                  |
| 3                  | email               | foo@bar.com         |
| 3                  | name                | John                |

## Technology Stack and Dependencies:

The webservies is implemented in python 2.7.11 with the [Flask](http://flask.pocoo.org/) framework and uses [SQlite 3](https://www.sqlite.org/) as a storage mechanism. Its dependencies include:
* [SQLAlchemy](http://www.sqlalchemy.org/) - a python ORM
* [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.1/) -  SQLAlchemy extension for flask
* [SQLAlchemy-migrate](https://sqlalchemy-migrate.readthedocs.org/en/latest/) - way to deal with database schema changes in SQLAlchemy projects

## File structure:
* **happy-commas** - the main folder of the project
  * **app** - the main directory of the project
    - **static/** - CSS files
    - **templates/** - html files
    - **exceptions.py** - define the InvalidUsage Exception class which is thrown on Error
    - **modeles.py** - define the Entry class around which the application is built.
    - **views.py** - define the import and export api endpoints
    - **utils.py** - a set of utility functions
  * **tmp** - temporary data storage
  * **db_repository** - historical information about database migrations and changes
  * **db_create.py, db_migrate, db_upgrade, db_downgrade** - a set of python scripts for managing the database
  * **run.py** - script for running the application in production
  * **runp.py** - script for running the application in debug mode
  * **tests.py** - application tests

## Database Management Scripts:
The python files with prefix **db_**  are a set of scripts that invoke database
management APIs and automate database migrations. These scripts use SQLAlchemy-migrate
package.The folder **db_repository** holds historical information about database migration and versioning.
In order to set up the database run:
```
$ ./db_create
```
If any changes to the structure of the database are applied run:
```
$ ./db_migrate
```
Every modification of the database is saved. Each change increments the database version with one. The folder db_repository/
hold information about the database changes and versions. If downgrading to previous version, run:
```
$ ./db_downgrade
```
If upgrading to upper version:
```
$ ./db_upgrade
```
## Tests:
In order to run the tests run:
```
$ ./tests.py
```
