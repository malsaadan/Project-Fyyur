#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for,
    abort
)
from models import db, Venue, Artist, Show
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
db.init_app(app)
moment = Moment(app)
app.config.from_object('config')

# To setup the migration
migrate = Migrate(app, db)

  

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# landing page controller
@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

# Venue list controller
@app.route('/venues')
def venues():
  # A variable to hold all data to be sent
  data = []

  # Used .distinct() to get unique values in the list. source: https://stackoverflow.com/questions/12897374/get-unique-values-from-a-list-in-python#12897477
  # all_locations holds all unique values of city and states to display the list of venues categorized by them
  all_locations = db.session.query(Venue.city, Venue.state).distinct()

  # loop over all_locations 
  for location in all_locations:
    # Get all venues filtered by specific location
    venues = Venue.query.filter_by(city=location.city).filter_by(state=location.state).all()
    group = []

    # Get the id, name and upcoming shows of the venue and append it to a location group
    for venue in venues:
      group.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == venue.id).all())
      })
    
    # Append all extracted info to data
    data.append({
      'city': location.city,
      'state': location.state,
      'venues': venues
    })
  
  return render_template('pages/venues.html', areas=data);


# Venue Search Controller
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Get the search term from the submitted form
  search_term = request.form.get('search_term', '')
  # Query all venues that contain the search term
  search_results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []
  # Append results to data
  for result in search_results:
    data.append({
        'id': result.id,
        'name': result.name,
        'num_upcoming_shows': len(result.shows.filter(show.start_time > datetime.now()))
      })

  response = {
    "count": len(search_results),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term = search_term)

# Display Venue Controller
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id 
  venue = Venue.query.get(venue_id)
  
  upcoming_shows = upcoming(Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == venue.id).all())
  past_shows = past(Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == venue.id).all())

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "upcoming_shows_count": len(upcoming_shows),
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "past_shows": past_shows

  }

  return render_template('pages/show_venue.html', venue=data)


#  Create Venue Controllers
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False

  try:
    # Instantiate an instance from the venue model and save all data submitted through the form in it
    venue = Venue(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    address = request.form['address'],
    phone = request.form['phone'],
    genres = request.form.getlist('genres'),
    website = request.form['website'],
    image_link = request.form['image_link'],
    facebook_link = request.form['facebook_link'],
    seeking_talent = True if 'seeking_talent' in request.form else False,
    seeking_description = request.form['seeking_description']
    )

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error has occurred. Venue '+request.form['name']+' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

# Delete Venue Controller
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue with id ' + venue_id + ' was successfully deleted!')
    return redirect(url_for('index'))
  except:
    flash('An error has occurred. Venue with id '+venue_id+' could not be deleted.')
    db.session.rollback()
    abort(400)
  finally:
    db.session.close()

#  Artists
#  ----------------------------------------------------------------

# Artists list controller
@app.route('/artists')
def artists():
  data=[]
  # Query all artists
  all_artists = Artist.query.all()
  # Append id and name of artist to the data to be sent
  for artist in all_artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })

  return render_template('pages/artists.html', artists=data)

# Artist Search Controller
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # Get search term
  search_term = request.form.get('search_term', '')
  # Query all matching terms
  search_results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  # Extract id, name and number of upcoming shows and append it to data
  for result in search_results:
    data.append({
        'id': result.id,
        'name': result.name,
        'num_upcoming_shows': len(artist.shows.filter(show.start_time > datetime.now()))
      })

  response = {
    'count': len(search_results),
    "data": data
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# Display Artist Controller
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # Query artist with the matched id
  artist = Artist.query.get(artist_id)

  upcoming_shows = upcoming(Show.query.filter(Show.start_time > datetime.now(), Show.artist_id == artist_id).all())
  past_shows = past(Show.query.filter(Show.start_time < datetime.now(), Show.artist_id == artist_id).all())

  data = {
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "upcoming_shows_count": len(upcoming_shows),
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "past_shows": past_shows
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

# Update Artist Controllers
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.website = request.form['website']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']
    
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error has occurred. Artist '+request.form['name']+' could not be updated.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))


# Update Venue Controllers
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.website = request.form['website']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()

  except:
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error has occurred. Venue '+request.form['name']+' could not be updated.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

# Create Artist Controllers
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False

  try:
    # Instantiate an instance of Artist Model and save all submitted data in it
    artist = Artist(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      image_link = request.form['image_link'],
      website = request.form['website'],
      facebook_link = request.form['facebook_link'],
      seeking_venue = True if 'seeking_venue' in request.form else False, 
      seeking_description = request.form['seeking_description']
    )

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  if error:
    flash('An error has occurred. Artist '+request.form['name']+' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
# Shows list Controller
@app.route('/shows')
def shows():
  data = []
  # Query all shows
  all_shows = Show.query.all()
  # Loop through all shows
  for show in all_shows:
    # Get id, name of the venue and artist associated with the shows and the artist image link + the start time of the show
    artist = Artist.query.get(show.artist_id)
    data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)

# Create Show Controllers
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  
  try:
    show = Show(
      venue_id = request.form['venue_id'],
      artist_id = request.form['artist_id'],
      start_time = request.form['start_time']
    )

    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  if error:
    flash('An error has occurred. Show could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')

  return render_template('pages/home.html')


# A method to get id, name and image link of artist associated with the show
def upcoming(shows):
  upcoming_shows = []
  for show in shows:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": str(show.start_time)
    })
  return upcoming_shows

# A method to get id, name and image link of artist associated with the show
def past(shows):
  past_shows = []
  for show in shows:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": str(show.start_time)
    })
  return past_shows


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
