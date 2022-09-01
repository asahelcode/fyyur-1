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
from datetime import datetime
from flask_migrate import Migrate
from sqlalchemy import TIMESTAMP, BOOLEAN, ARRAY, and_
import sys
from models import * 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)  
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database


# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  all_venues =Venue.query.all()
  data = []
  state =[] 
  city = []

  for venue in all_venues:
    venue_info={}
    venue_info['venues'] = []
    venue_info['city'] = venue.city
    venue_info['state'] = venue.state

    if venue_info['city'] in city and venue_info['state'] in state:
      continue
    
    city.append(venue.city)
    state.append(venue.state)

    venue_list = Venue.query.\
    filter(and_(Venue.city == venue_info['city'], 
    Venue.state == venue_info['state'])).all()

    for venue in venue_list:
      num_upcoming_shows = len(get_upcoming_show(venue.artists))
      venue_info['venues'].\
      append({'id': venue.id, 'name': venue.name,
       'num_upcoming_shows': num_upcoming_shows})

    data.append(venue_info)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  #Get the search term
  search_term = request.form.get('search_term')

  data =[]

  match_venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  for venue in match_venues:
    item = {}
    item['id'] = venue.id
    item['name'] = venue.name

    shows = venue.artists
    if len(upcoming_shows) >= 1:
      upcoming_shows = [show.start_time > datetime.now() for show in shows]
    
    item['num_upcoming_show'] = len(upcoming_shows)

    data.append(item)

  response={
    "count": len(match_venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response,
   search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  current_venue = Venue.query.filter(Venue.id == venue_id).one()
  
  data = {
    'id': current_venue.id,
    'name': current_venue.name,
    'genres': current_venue.genres,
    'city': current_venue.city,
    'state': current_venue.state,
    'address': current_venue.address,
    'phone': current_venue.phone,
    'website': current_venue.websitelink,
    'facebook_link': current_venue.facebook_link,
    'seeking_talent': current_venue.seeking_talent,
    'seeking_description': current_venue.seeking_description,
    'image_link': current_venue.image_link
  }


  upcoming_shows_query = db.session.query(Show).join(Venue).\
  filter(Show.venue_id == current_venue.id).\
  filter(Show.start_time  > datetime.now()).all()

  for show in upcoming_shows_query:
    upcoming_shows.append(show)

  past_shows_query = db.session.query(Show).join(Venue).\
  filter(Show.venue_id == current_venue.id).\
  filter(Show.start_time  <= datetime.now()).all()

  for show in past_shows_query:
    past_shows.append(show)


  data['upcoming_shows'] = []
  data['past_shows'] = []

  if len(upcoming_shows) >= 1:
    for show in upcoming_shows:
      artist = show.artists
      data['upcoming_shows'].append({'artist_id':artist.id,
       'artist_name': artist.name, 'artist_image_link': artist.image_link,
        'start_time': str(show.start_time)})


  if len(past_shows) >= 1:
    for show in past_shows:
      artist = show.artists
      data['upcoming_shows'].append({'artist_id':artist.id,
       'artist_name': artist.name, 'artist_image_link': artist.image_link,
        'start_time': str(show.start_time)})

  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form)
  # TODO: modify data to be the data object returned from db insertion

  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  address = form.address.data
  facebook_link = form.facebook_link.data
  image_link = form.image_link.data
  websitelink = form.website_link.data
  seeking_talent = form.seeking_talent.data
  seeking_description = form.seeking_description.data
  error = False
  try:
    venue = Venue(name=name, city=city, state=state, phone=phone,
        genres=genres, 
    facebook_link=facebook_link,address=address,  websitelink=websitelink,
        image_link=image_link, 
      seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()

  if not error:
  # on successful db insert, flash success
    flash('Venue ' + name + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  else:
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue_to_delete = Venue.query.filter(Venue.id == venue_id).one()

  try:
    db.session.delete(venue_to_delete)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  all_artists = Artist.query.all()
  data = []

  for artist in all_artists:
    data.append({'id': artist.id, 'name': artist.name})

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term')

  data =[]
  upcoming_shows = []

  match_artists = Artist.query.\
  filter(Artist.name.ilike(f'%{search_term}%')).all()

  for artist in match_artists:
    item = {}
    item['id'] = artist.id
    item['name'] = artist.name

    shows = artist.venues
    if len(upcoming_shows) >= 1:
      upcoming_shows = get_upcoming_show(shows)

    item['num_upcoming_show'] = len(upcoming_shows)

    data.append(item)

  response={
    "count":len(match_artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  current_artist = Artist.query.filter(Artist.id == artist_id).one()
  data = {
    'id': current_artist.id,
    'name': current_artist.name,
    'genres': current_artist.genres,
    'city': current_artist.city,
    'state': current_artist.state,
    'phone': current_artist.phone,
    'website': current_artist.websitelink,
    'facebook_link': current_artist.facebook_link,
    'seeking_venue': current_artist.seeking_venue,
    'seeking_description': current_artist.seeking_description,
    'image_link': current_artist.image_link
  }

  upcoming_shows = []
  past_shows = []

  upcoming_shows_query = db.session.query(Show).join(Artist).\
  filter(Show.artist_id == current_artist.id).\
  filter(Show.start_time  > datetime.now()).all()

  print(upcoming_shows_query)

  for show in upcoming_shows_query:
    upcoming_shows.append(show)

  past_shows_query = db.session.query(Show).join(Artist).\
  filter(Show.artist_id == current_artist.id).\
  filter(Show.start_time  <= datetime.now()).all()

  for show in past_shows_query:
    past_shows.append(show)

  data['upcoming_shows'] = []
  data['past_shows'] = []

  if len(upcoming_shows) >= 1:
    for show in upcoming_shows:
      venue = show.venues
      data['upcoming_shows'].append({'venue_id':venue.id,
       'venue_name': venue.name, 'venue_image_link': venue.image_link, 
       'start_time': str(show.start_time)})


  if len(past_shows) >= 1:
    for show in past_shows:
      venue = show.venues
      data['past_shows'].\
      append({'venue_id':venue.id, 'venue_name': venue.name,
       'venue_image_link': venue.image_link,
        'start_time': str(show.start_time)})

  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  #Pray it worrks
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  current_artist_to_edit = Artist.query.filter(Artist.id == artist_id).one()

  form.name.data = current_artist_to_edit.name
  form.genres.data = current_artist_to_edit.genres
  form.city.data = current_artist_to_edit.city
  form.state.data = current_artist_to_edit.state
  form.phone.data = current_artist_to_edit.phone
  form.website_link.data = current_artist_to_edit.websitelink
  form.facebook_link.data = current_artist_to_edit.facebook_link
  form.seeking_venue.data = current_artist_to_edit.seeking_venue
  form.seeking_description.data = current_artist_to_edit.seeking_description
  form.image_link.data = current_artist_to_edit.image_link
  
  artist={
    "id": current_artist_to_edit.id,
    "name": current_artist_to_edit.name,
    "genres": current_artist_to_edit.genres,
    "city": current_artist_to_edit.city,
    "state":current_artist_to_edit.state,
    "phone": current_artist_to_edit.phone,
    "website": current_artist_to_edit.websitelink,
    "facebook_link": current_artist_to_edit.facebook_link,
    "seeking_venue": current_artist_to_edit.seeking_venue,
    "seeking_description": current_artist_to_edit.seeking_description,
    "image_link": current_artist_to_edit.image_link
  }

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm()

  current_artist_to_edit = Artist.query.filter(Artist.id == artist_id).one()

  # current_artist_to_edit.name = form.name.data
  # current_artist_to_edit.city = form.city.data
  # current_artist_to_edit.state = form.state.data
  # current_artist_to_edit.phone = form.phone.data
  # current_artist_to_edit.genres = form.genres.data
  # current_artist_to_edit.facebook_link = form.facebook_link.data
  # current_artist_to_edit.image_link = form.image_link.data
  # current_artist_to_edit.websitelink = form.website_link.data
  # current_artist_to_edit.seeking_venue = form.seeking_venue.data
  # current_artist_to_edit.seeking_description = form.seeking_description.data

  try:
    current_artist_to_edit = Artist()
    form.populate_obj(current_artist_to_edit)
    db.session.add(current_artist_to_edit)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  current_venue_to_edit = Venue.query.filter(Venue.id == venue_id).one()

  form.name.data = current_venue_to_edit.name
  form.genres.data = current_venue_to_edit.genres
  form.address.data = current_venue_to_edit.address
  form.city.data = current_venue_to_edit.city
  form.state.data = current_venue_to_edit.state
  form.phone.data = current_venue_to_edit.phone
  form.website_link.data = current_venue_to_edit.websitelink
  form.facebook_link.data = current_venue_to_edit.facebook_link
  form.seeking_talent.data = current_venue_to_edit.seeking_talent
  form.seeking_description.data = current_venue_to_edit.seeking_description
  form.image_link.data = current_venue_to_edit.image_link
  
  venue={
    "id": current_venue_to_edit.id,
    "name": current_venue_to_edit.name,
    "genres": current_venue_to_edit.genres,
    "address": current_venue_to_edit.address,
    "city": current_venue_to_edit.city,
    "state":current_venue_to_edit.state,
    "phone": current_venue_to_edit.phone,
    "website": current_venue_to_edit.websitelink,
    "facebook_link": current_venue_to_edit.facebook_link,
    "seeking_talent": current_venue_to_edit.seeking_talent,
    "seeking_description": current_venue_to_edit.seeking_description,
    "image_link": current_venue_to_edit.image_link
  }

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()

  current_venue_to_update = Venue.query.filter(Venue.id == venue_id).one()

  # current_venue_to_update.name = form.name.data
  # current_venue_to_update.city = form.city.data
  # current_venue_to_update.state = form.state.data
  # current_venue_to_update.address = form.address.data
  # current_venue_to_update.phone = form.phone.data
  # current_venue_to_update.genres = form.genres.data
  # current_venue_to_update.facebook_link = form.facebook_link.data
  # current_venue_to_update.image_link = form.image_link.data
  # current_venue_to_update.websitelink = form.website_link.data
  # current_venue_to_update.seeking_talent = form.seeking_talent.data
  # current_venue_to_update.seeking_description = form.seeking_description.data

  try:
    current_venue_to_update = Venue()
    form.populate_obj(current_venue_to_update)
    db.session.add(current_venue_to_update)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

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
  # TODO: insert form data as a new Venue record in the db, instead

  form = ArtistForm(request.form)
  # TODO: modify data to be the data object returned from db insertion
  
  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  facebook_link = form.facebook_link.data
  image_link = form.image_link.data
  websitelink = form.website_link.data
  seeking_venue = form.seeking_venue.data
  seeking_description = form.seeking_description.data
  print(genres)
  error = False
  try:
    artist = Artist(name=name, city=city, state=state,
     phone=phone, genres=genres, 
    facebook_link=facebook_link, websitelink=websitelink,
     image_link=image_link, 
    seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()

  if not error:
      # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # # TODO: on unsuccessful db insert, flash an error instead.
  else:
    flash('An error occurred. Artist ' + name + 'could not be listed.')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  artists = Artist.query.all()
  data = []
  
  for artist in artists:
    show_info = {}
    show_info['artist_id'] = artist.id
    show_info['artist_name'] = artist.name
    shows = artist.venues # Returns venues show for artist

    for show in shows:
      show_info = {}
      show_info['start_time'] = str(show.start_time)
      show_info['venue_id'] = show.venues.id
      show_info['venue_name'] = show.venues.name
      if len(shows) >= 1:
        show_info['artist_id'] = artist.id
        show_info['artist_name'] = artist.name
        show_info['artist_image_link'] = artist.image_link
        data.append(show_info)
      else:
        data.append(show_info)

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

  show_form = ShowForm(request.form)

  artist_id = show_form.artist_id.data
  venue_id = show_form.venue_id.data
  start_time = show_form.start_time.data

  #Fetch artist by its id to attach to a show
  artist = Artist.query.filter(Artist.id == artist_id).one()
  #Fetch venue to attach to a particular show
  venue = Venue.query.filter(Venue.id == venue_id).one()


  error = False
  try:
    show = Show(venue_id=venue_id, start_time=start_time, artist_id=artist_id)

    show.artists = artist # Attach artist to a particular show
    show.venues = venue # Attach venue to a particular show
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback() # cancels the transaction incase of failure
    print(sys.exc_info())
    error = True

  finally:
    db.session.close()

  if error:
    flash(f'an error occurred. {name} could not be listed')
  else:
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
        Formatter('%(asctime)s %(levelname)s:\
         %(message)s [in %(pathname)s:%(lineno)d]')
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
