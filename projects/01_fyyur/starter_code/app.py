#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import date

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__, instance_relative_config=True)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    show = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return (f'<Venue ID: {self.id}, name: {self.name}, city: {self.city},' 
        f' state: {self.state}, address: {self.address}, phone: {self.phone},' 
        f' genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}>')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    show = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return (f'<Artist ID: {self.id}, name: {self.name}, city: {self.city},' 
        f' state: {self.state}, phone: {self.phone},' 
        f' genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}>')

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime(), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

  def __repr__(self):
    return (f'<Show ID: {self.id}, start_time: {self.start_time}, venue_id: {self.venue_id}, artist_id: {self.artist_id}>')


db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  raw_data = Venue.query.all()
  temp_data = []
  for row in raw_data:
    temp_data.append({"city": row.city, "state": row.state, "venues": [{"id": row.id, "name": row.name}]})

  data = []
  for venue in temp_data:
    if(len(data) == 0):
      venue['venues'][0]['num_upcoming_shows'] = 0
      data.append(venue)
    else:
      i = 0
      inserted = False
      for row in data:
        if (venue['city'] == row['city']) and (venue['state'] == row['state']):
          venue['venues'][0]['num_upcoming_shows'] = len(row['venues'])
          data[i]['venues'].append(venue['venues'][0])
          inserted = True
        i += 1
      if inserted == False:
        venue['venues'][0]['num_upcoming_shows'] = 0
        data.append(venue)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  response = {}
  response['data'] = []
  i = 1
  for venue in venues:
    response['count'] = i
    response['data'].append({'id': venue.id, 'name': venue.name})
    i += 1

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()
  past_shows = []
  upcoming_shows = []
  for show in shows:
    if show.start_time.date() > date.today():
      upcoming_shows.append({"artist_id": show.artist_id, "artist_name": show.artist.name, 
        "artist_image_link": show.artist.image_link, "start_time" :str(show.start_time)})
    else:
      past_shows.append({"artist_id": show.artist_id, "artist_name": show.artist.name, 
        "artist_image_link": show.artist.image_link, "start_time" :str(show.start_time)})

  data = {    
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres[1:-1].split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
    }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if form.validate_on_submit():
    try:
      venue = Venue(name=request.form['name'], 
                    city=request.form['city'], 
                    state=request.form['state'],
                    address=request.form['address'], 
                    phone=request.form['phone'], 
                    genres=request.form.getlist('genres'), 
                    facebook_link=request.form['facebook_link'])
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      db.session.rollback()
    finally:
      db.session.close()
    return render_template('pages/home.html')
  else:
    flash(f'Failed due to the following validation error(s) : {form.errors}')
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id) 
    db.session.delete(venue) 
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({"id": artist.id, "name": artist.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  response = {}
  response['data'] = []
  i = 1
  for artist in artists:
    response['count'] = i
    response['data'].append({'id': artist.id, 'name': artist.name})
    i += 1

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).all()
  past_shows = []
  upcoming_shows = []
  for show in shows:
    if show.start_time.date() > date.today():
      upcoming_shows.append({"venue_id": show.venue_id, "venue_name": show.venue.name, 
        "venue_image_link": show.venue.image_link, "start_time" :str(show.start_time)})
    else:
      past_shows.append({"venue_id": show.venue_id, "venue_name": show.venue.name, 
        "venue_image_link": show.venue.image_link, "start_time" :str(show.start_time)})

  data = {    
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres[1:-1].split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
    }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)
  if form.validate_on_submit():
    try:
      artist.name = request.form['name']
      artist.city = request.form['city']
      artist.state = request.form['state']
      artist.phone = request.form['phone']
      artist.genres = request.form.getlist('genres')
      artist.facebook_link = request.form['facebook_link']
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except Exception:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
      db.session.rollback()
    finally:
      db.session.close()
      return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    flash(f'Failed due to the following validation error(s) : {form.errors}')
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  if form.validate_on_submit():
    try:
      venue.name = request.form['name']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.phone = request.form['phone']
      venue.genres = request.form.getlist('genres')
      venue.facebook_link = request.form['facebook_link']
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except Exception:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
      db.session.rollback()
    finally:
      db.session.close()
      return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    flash(f'Failed due to the following validation error(s) : {form.errors}')
    return render_template('forms/edit_venue.html', form=form, venue_id=venue_id)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  if form.validate_on_submit():
    try:
      artist = Artist(name=request.form['name'], 
                      city=request.form['city'], 
                      state=request.form['state'],
                      phone=request.form['phone'], 
                      genres=request.form.getlist('genres'), 
                      facebook_link=request.form['facebook_link'])
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
    finally:
      db.session.close()

    return render_template('pages/home.html')
  else:
    flash(f'Failed due to the following validation error(s) : {form.errors}')
    return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({'venue_id': show.venue_id, 'venue_name': show.venue.name, 'artist_id': show.artist_id, 
      'artist_name': show.artist.name, 'artist_image_link': show.artist.image_link, 'start_time': str(show.start_time)})

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    show = Show(venue_id=request.form['venue_id'], artist_id=request.form['artist_id'], 
      start_time=request.form['start_time'])
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as e:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

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
