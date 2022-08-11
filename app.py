#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import logging
from flask import render_template, request, Response, flash, redirect, url_for
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from init import *
from models import *
from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import desc
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# connection to postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

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
    # data=[{
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "venues": [{
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "num_upcoming_shows": 0,
    #   }, {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "num_upcoming_shows": 1,
    #   }]
    # }, {
    #   "city": "New York",
    #   "state": "NY",
    #   "venues": [{
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "num_upcoming_shows": 0,
    #   }]
    # }]
    
    all_venues_info = Venue.query.order_by(Venue.city).with_entities(Venue.city, Venue.state)\
                  .group_by(Venue.city, Venue.state).all()
    
    data = []
    
    for venue in all_venues_info:
        data.append({ "city": venue.city, "state": venue.state})
        
    for item in data:
        item['venues'] = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.city==item.get('city')).all()
        # item['venues'] = []
    
    # for venue in all_venues:
    #     data.append({"city": venue.city,
    #                   "state": venue.state,
    #                   "venues": [{
    #                     "id": venue.id,
    #                     "name": venue.name
    #                   }]
    #                 })

    
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_word = request.form.get('search_term', '')
  
  response={
    "count": Venue.query.filter(Venue.name.ilike(f'%{search_word}%')).count(),
    "data": Venue.query.filter(Venue.name.ilike(f'%{search_word}%')).all()
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    data = Venue.query.get(venue_id)
    
    all_shows = Show.query.join(Venue, Show.venue_id==Venue.id)\
                .join(Artist, Show.artist_id==Artist.id).all()
    
    data.past_shows = []
    data.upcoming_shows = []
    
    for show in all_shows:
        # print(show.artist)
        # loop throught the show, check if the single venue has a show
        if show.venue_id == data.id:
            # print(show.start_time > datetime.now()) 
            if show.start_time > datetime.now():
                data.upcoming_shows.append({"artist_id": show.artist_id,
                                            "artist_name": show.artist.name,
                                            "artist_image_link": show.artist.image_link,
                                            "start_time": format_datetime(str(show.start_time))
                                            })
            else:
                data.past_shows.append({"artist_id": show.artist_id,
                                        "artist_name": show.artist.name,
                                        "artist_image_link": show.artist.image_link,
                                        "start_time": format_datetime(str(show.start_time))
                                        })
    
    data.past_shows_count = len(data.past_shows)
    data.upcoming_shows_count = len(data.upcoming_shows)
    
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        venue = Venue()
        form = VenueForm(request.form, obj=venue)
        
        if form.validate():
            form.populate_obj(venue)
            
            db.session.add(venue)
            db.session.commit()
            
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('venues'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_word = request.form.get('search_term', '')
  
  response={
    "count": Artist.query.filter(Artist.name.ilike(f'%{search_word}%')).count(),
    "data": Artist.query.filter(Artist.name.ilike(f'%{search_word}%')).all()
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = Artist.query.get(artist_id)
    
    all_shows = Show.query.join(Artist, Show.artist_id==Artist.id)\
                .join(Venue, Show.venue_id==Venue.id).all() 
    
    data.past_shows = []
    data.upcoming_shows = []
    
    for show in all_shows:
        if show.artist_id == data.id:
            if show.start_time > datetime.now():
                data.upcoming_shows.append({
                                        "venue_id": show.venue_id,
                                        "venue_name": show.venue.name,
                                        "venue_image_link": show.venue.image_link,
                                        "start_time": format_datetime(str(show.start_time))
                                      })
            else:
                data.past_shows.append({
                                        "venue_id": show.venue_id,
                                        "venue_name": show.venue.name,
                                        "venue_image_link": show.venue.image_link,
                                        "start_time": format_datetime(str(show.start_time))
                                      })
    
    data.past_shows_count = len(data.past_shows)
    data.upcoming_shows_count = len(data.upcoming_shows)
    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    
    artist={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website_link": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
    }
    
    form = ArtistForm(data=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        form = ArtistForm(request.form, obj=artist)
        if form.validate():
            form.populate_obj(artist)
            
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('An error occurred. Update Artist ' + request.form['name'] + ' was failed.')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    
    venue={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website_link": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link
    }
    
    form = VenueForm(data=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        form = VenueForm(request.form, obj=venue)
        if form.validate():
            form.populate_obj(venue)
            
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('An error occurred. Update Venue ' + request.form['name'] + ' was failed.')
    finally:
        db.session.rollback()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        artist = Artist()
        form = ArtistForm(request.form, obj=artist)
        
        if form.validate():
            form.populate_obj(artist)
            
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('artists'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    all_shows = Show.query.join(Artist, Show.artist_id==Artist.id)\
                .join(Venue, Show.venue_id==Venue.id)\
                .order_by(desc(Show.start_time))\
                .limit(10).all()
    
    data = []
    
    for show in all_shows:
        print(show.artist)
        data.append({
                    "venue_id": show.venue_id,
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "venue_name": show.venue.name,
                    "start_time": format_datetime(str(show.start_time))
                    })
        
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        show = Show()
        form = ShowForm(request.form, obj=show)
        
        if form.validate():
            form.populate_obj(show)
            
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
    except:
          db.session.rollback()
          flash('An error occurred. Show could not be listed.')
    finally:
          db.session.close()
    return redirect(url_for('index'))

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
