import os
import pwd

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
# Got the username from the system itself, reference used: https://stackoverflow.com/questions/842059/is-there-a-portable-way-to-get-the-current-username-in-python
SQLALCHEMY_DATABASE_URI = f'postgres://{pwd.getpwuid(os.getuid())[0]}@localhost:5432/fyyur-app'
print(SQLALCHEMY_DATABASE_URI)
