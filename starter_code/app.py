# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from datetime import datetime
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database                ####################3## done ################

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", backref='venues', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate  ######## may done ###


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", backref='artists', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate    ###### may done ###
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')                                                ################  done  ################
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    venues_list = Venue.query.all()

    data = []
    selected_venues_id = []
    for i in range(len(venues_list)):
        venues = []
        _venue = venues_list[i]
        if _venue.id not in selected_venues_id:
            city = _venue.city
            state = _venue.state
            selected_venues_id.append(_venue.id)
            venues.append(_venue)
            for j in range(i+1, len(venues_list)):
                venue = venues_list[j]
                if (venue.state == state) and (venue.city.find(city) >= 0) :

                    selected_venues_id.append(venue.id)
                    venues.append(venue)

            data.append({
                "city": city,
                "state": state,
                "venues": venues
             })

    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])                    ###################     done   ##############
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    #  seach for Hop should return "The Musical Hop".
    #  search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    count = 0
    search_result = []
    search_data = request.form.get('search_term')
    venues_list = Venue.query.all()
    for venue in venues_list:
        if venue.name.find(search_data) >= 0:
            count += 1
            search_result.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": 0,
            })

    response = {
        "count": count,
        "data": search_result
    }

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')                       #################  done #######################
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    past_shows = []
    upcoming_shows = []
    upcoming_shows_count = 0
    past_shows_count = 0

    venue = Venue.query.get(venue_id)

    for show in venue.shows:
        artists = show.artists
        if show.start_time >= datetime.today():
            upcoming_shows_count += 1
            upcoming_shows.append({
                "id": artists.id,
                "name": artists.name,
                "venue_image_link": artists.image_link,
                "start_time": show.start_time
            })
        else:
            past_shows_count += 1
            past_shows.append({
                "id": artists.id,
                "name": artists.name,
                "venue_image_link": artists.image_link,
                "start_time": show.start_time.strftime("%Y/%m/%d/, %H:%M:%S")
            })

    data = {
        "id": venue_id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,

        "seeking_venue": venue.seeking_talent,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])                   ##################### done ##################
def create_venue_submission():
    data = request.form
    genres_list = data.getlist('genres')
    venue = Venue(name=data['name'], city=data['city'], state=data['state'], address=data['address'],
                  phone=data['phone'], genres=genres_list, facebook_link=data['facebook_link'])

    db.session.add(venue)

    try:
        db.session.commit()

        # TODO: insert form data as a new Venue record in the db, instead
        # TODO: modify data to be the data object returned from db insertion
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        return
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])                ######################   done  #############
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    #  SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.get(venue_id).delete()
        db.session.commit()
        flash('Venue was deleted successfully', 'success')
    except:
        flash('Venue was not deleted ', 'fail')

    #  BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    #  clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')                                           #################  done   ###############
def artists():
    # TODO: replace with real data returned from querying the database
    data = []
    artists = Artist.query.all()
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])                             #################  done  ########
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    count = 0

    search_result = []
    search_data = request.form.get('search_term').lower()
    artist_list = Artist.query.all()
    for artist in artist_list:
        if artist.name.lower().find(search_data) >= 0:
            count += 1
            upcoming_shows = 0
            for show in artist.shows:
                if show.start_time >= datetime.today():
                    upcoming_shows += 1

            search_result.append({
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": upcoming_shows
            })

    response = {
        "count": count,
        "data": search_result
    }

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')                               ####################  done ############
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    past_shows = []
    upcoming_shows = []
    artist = Artist.query.get(artist_id)

    upcoming_shows_count = 0
    past_shows_count = 0
    for show in artist.shows:
        venues = show.venues
        if show.start_time >= datetime.today():
            upcoming_shows_count += 1
            upcoming_shows.append({
                "id": venues.id,
                "name": venues.name,
                "venue_image_link": venues.image_link,
                "start_time": show.start_time
            })
        else:
            past_shows_count += 1
            past_shows.append({
                "id": venues.id,
                "name": venues.name,
                "venue_image_link": venues.image_link,
                "start_time": show.start_time.strftime("%Y/%m/%d/, %H:%M:%S")
            })


    data = {
        "id": artist_id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": artist.seeking_talent,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])              ##########  done ###########
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])        ########### done ######################
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    #  artist record with ID <artist_id> using the new attributes
    data = request.form
    artist = Artist.query.get(artist_id)

    # artist.id = artist_id
    artist.name = data['name']
    artist.genres = data['genres']
    artist.city = data['city']
    artist.state = data['state']
    artist.phone = data['phone']
    artist.facebook_link = data['facebook_link']

    # artist.website = data['website']
    # artist.seeking_talent = data['seeking_talent']
    # artist.seeking_description = data['seeking_description']
    # artist.image_link = data['image_link']

    db.session.commit()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])      #############    done  #####################
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])         ################ done ####################
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    data = request.form
    venue = Venue.query.get(venue_id)

    venue.name = data['name']
    venue.genres = data['genres']
    venue.address = data['address']
    venue.city = data['city']
    venue.state = data['state']
    venue.phone = data['phone']
    venue.facebook_link = data['facebook_link']

    # venue.website = data['website']
    # venue.seeking_talent = data['seeking_talent']
    # venue.seeking_description = data['seeking_description']
    # venue.image_link = data['image_link']

    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])                     ############  done #################
def create_artist_submission():
    data = request.form
    genres_list = data.getlist('genres')
    artist = Artist(name=data['name'], city=data['city'], state=data['state'],
                    phone=data['phone'], genres=genres_list[0], facebook_link=data['facebook_link'])

    db.session.add(artist)

    try:
        db.session.commit()

        # TODO: insert form data as a new Artist record in the db, instead
        # TODO: modify data to be the data object returned from db insertion
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        return None

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')                                                #################### done #################
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    show_list = Show.query.all()
    # print(format_datetime(str(show_list[0].start_time)))
    for show in show_list:

        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venues.name,
            "artist_id": show.artist_id,
            "artist_name": show.artists.name,
            "artist_image_link": show.artists.image_link,
            "start_time": show.start_time.strftime("%Y/%m/%d/, %H:%M:%S")
         })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])                     ##############   done   #####################
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    data = request.form

    show = Show(artist_id=data['artist_id'], venue_id=data['venue_id'], start_time=data['start_time'])

    try:
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return None

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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
