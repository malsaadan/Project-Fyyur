#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
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
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# To setup the migration
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue Id:{self.id} name:{self.name} shows:{self.shows}'

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist Id:{self.id} name:{self.name} shows:{self.shows}'


class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
    return f'Show Id:{self.id} venue_id:{self.venue_id} artist_id:{self.artist_id} time:{self.start_time}'
  

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

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []

  # Used .distinct() to get unique values in the list. source: https://stackoverflow.com/questions/12897374/get-unique-values-from-a-list-in-python#12897477
  all_locations = db.session.query(Venue.city, Venue.state).distinct()

  for location in all_locations:
    venues = Venue.query.filter_by(city=location.city).filter_by(state=location.state).all()
    group = []

    for venue in venues:
      group.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()
      })
    
    data.append({
      'city': location.city,
      'state': location.state,
      'venues': venues
    })
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  search_results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []
  for result in search_results:
    data.append({
        'id': result.id,
        'name': result.name,
        'num_upcoming_shows': Show.query.filter_by(venue_id=result.id).filter(Show.start_time > datetime.now()).count()
      })

  response = {
    'count': len(search_results),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term = search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id 
  data = Venue.query.filter_by(id=venue_id).first()
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False

  try:
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
@app.route('/artists')
def artists():
  data=[]
  all_artists = Artist.query.all()
  for artist in all_artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  search_results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  for result in search_results:
    data.append({
        'id': result.id,
        'name': result.name,
        'num_upcoming_shows': Show.query.filter_by(artist_id=result.id).filter(Show.start_time > datetime.now()).count()
      })

  response = {
    'count': len(search_results),
    "data": data
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.filter_by(id=artist_id).first()

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
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

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False

  try:
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

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  all_shows = Show.query.all()
  for show in all_shows:
    venue = show.venue_id
    artist = show.artist_id
    data.append({
      "venue_id": venue,
      "vanue_name": Venue.query.get(venue).name,
      "artist_id": artist,
      "artist_name": Artist.query.get(artist).name,
      "artist_image_link": Artist.query.get(artist).image_link,
      "start_time": show.start_time
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
