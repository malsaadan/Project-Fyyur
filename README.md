Fyyur
-----
This project was built as a requirement in Misk Academy-Udacity Full-Stack Developer Nanodegree.


### Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

Your job is to build out the data models to power the API endpoints for the Fyyur site by connecting to a PostgreSQL database for storing, querying, and creating information about artists and venues on Fyyur.

### User Stories

* As a user, I want to create a new venue.
* As a user, I want to see all venues categorized by city and state.
* As a user, I want to be able to search for venues by name.
* As a user, I want to see all venue's details.
* As a user, I want to be able to edit a venue.
* As a user, I want to be able to delete a venue.
* As a user, I want to create a new artist.
* As a user, I want to a list of all artists.
* As a user, I want to be able to search for artists by name.
* As a user, I want to see all details of an artist.
* As a user, I want to be able to edit an artist.
* As a user, I want to create a new show.
* As a user, I want to see all shows.

### Tech Stack

Our tech stack will include:

* **SQLAlchemy ORM** to be our ORM library of choice
* **PostgreSQL** as our database of choice
* **Python3** and **Flask** as our server language and server framework
* **Flask-Migrate** for creating and running schema migrations
* **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/) for our website's frontend

### Main Files: Project Structure

  ```sh
  ├── README.md
  ├── app.py *** the main driver of the app. Includes your SQLAlchemy models.
                    "python app.py" to run after installing dependences
  ├── config.py *** Database URLs, CSRF generation, etc
  ├── error.log
  ├── forms.py *** Your forms
  ├── requirements.txt *** The dependencies we need to install with "pip3 install -r requirements.txt"
  ├── static
  │   ├── css 
  │   ├── font
  │   ├── ico
  │   ├── img
  │   └── js
  └── templates
      ├── errors
      ├── forms
      ├── layouts
      └── pages
  ```

### Future Work

* Implement time availability, so that an artist is only available to be booked at certain dates/times. Disable the ability to create book an artist for a show outside of their availability.

* Show Recent Listed Artists and Recently Listed Venues on the homepage, returning results for Artists and Venues sorting by newly created. Limit to the 10 most recently listed items.

* Showcase what albums and songs an artist has on the Artist’s page.