# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import sys
from collections import defaultdict
from forms import *
from flask_wtf import Form
from logging import Formatter, FileHandler
import logging
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
import json
import dateutil.parser
from babel import dates
from flask import Flask, render_template, request, Response, flash, \
    redirect, url_for, jsonify
from models import setup_db, db, Venue, Artist, Show
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
setup_db(app)


migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per
    # venue.

    all_venue = Venue.query.all()
    grouped_venue_data = group_venue_data(all_venue)
    return render_template('pages/venues.html', areas=grouped_venue_data)


def group_venue_data(venue_data):
    temp_dict = defaultdict(list)
    for v in venue_data:
        temp_dict[v.city].append(v)
    grouped_venue = []
    for value in temp_dict:
        a_dict = {}
        a_dict['city'] = value
        a_dict['state'] = temp_dict[value][0].state
        a_dict['venues'] = temp_dict[value]
        grouped_venue.append(a_dict)
    return grouped_venue


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search.
    # Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and
    # "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term')

    query_result = Venue.query.filter(
        Venue.name.ilike(f"%{search_term}%")).all()
    response = {}
    response['count'] = len(query_result)
    response['data'] = query_result
    # flash()
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)
    now = datetime.now()
    past_shows = []
    upcoming_shows = []
    for show in venue.shows:
        temp = {}
        temp_artist = Artist.query.get(show.artist_id)
        temp['artist_id'] = show.artist_id
        temp['artist_name'] = temp_artist.name
        temp['artist_image_link'] = temp_artist.image_link
        temp['start_time'] = show.start_time
        if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') < now:
            past_shows.append(temp)
        else:
            upcoming_shows.append(temp)
    data = venue
    setattr(data, 'past_shows', past_shows)
    setattr(data, 'past_shows_count', len(past_shows))
    setattr(data, 'upcoming_shows', upcoming_shows)
    setattr(data, 'upcoming_shows_count', len(upcoming_shows))
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
    # TODO: modify data to be the data object returned from db insertion
    try:
        venue_name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        facebook_link = request.form['facebook_link']
        image_link = request.form['image_link']
        website = request.form['website']
        seeking_talent = True \
            if request.form['seeking_talent'] == 'Yes' else False
        seeking_description = request.form['seeking_description']
        new_venue = Venue(
            name=venue_name,
            genres=genres,
            city=city,
            state=state,
            address=address,
            phone=phone,
            image_link=image_link,
            facebook_link=facebook_link,
            website=website,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description)
        db.session.add(new_venue)
        db.session.commit()
        flash(f"Venue {venue_name} was successfully listed! ")

    except BaseException:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be
        # listed.')
        db.session.rollback()
        flash(f'An error occurred. Venue {venue_name} could not be listed.')
    finally:
        db.session.close()

    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit
    # could fail.
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash("The venue is successfully deleted from database!")
    except BaseException:
        db.session.rollback()
        flash("Error deleting the venue!")
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page,
    # have it so that clicking that button delete it from the db then redirect
    # the user to the homepage
    return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    all_artists = Artist.query.all()
    return render_template('pages/artists.html', artists=all_artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure
    # it is case-insensitive. seach for "A" should return "Guns N Petals",
    # "Matt Quevado", and "The Wild Sax Band". search for "band" should
    # return "The Wild Sax Band".

    search_term = request.form.get('search_term')

    query_result = Artist.query.filter(
        Artist.name.ilike(f"%{search_term}%")).all()
    response = {}
    response['count'] = len(query_result)
    response['data'] = query_result
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)

    now = datetime.now()
    past_shows = []
    upcoming_shows = []
    for show in artist.shows:
        temp = {}
        temp_venue = Venue.query.get(show.venue_id)
        temp['venue_id'] = show.venue_id
        temp['venue_name'] = temp_venue.name
        temp['venue_image_link'] = temp_venue.image_link
        temp['start_time'] = show.start_time
        if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') < now:
            past_shows.append(temp)
        else:
            upcoming_shows.append(temp)
    data = artist
    setattr(data, 'past_shows', past_shows)
    setattr(data, 'past_shows_count', len(past_shows))
    setattr(data, 'upcoming_shows', upcoming_shows)
    setattr(data, 'upcoming_shows_count', len(upcoming_shows))

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)
    form.name.default = artist.name
    form.city.default = artist.city
    form.state.default = artist.state
    form.phone.default = artist.phone
    form.genres.default = artist.genres
    form.website.default = artist.website
    form.facebook_link.default = artist.facebook_link
    form.image_link.default = artist.image_link
    form.seeking_venue.default = "Yes" if artist.seeking_venue else "No"
    form.seeking_description.default = artist.seeking_description
    form.process()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website = request.form['website']
    artist.seeking_venue = True \
        if request.form['seeking_venue'] == 'Yes' else False
    artist.seeking_description = request.form['seeking_description']

    try:
        db.session.commit()
        flash(f"Artist {artist.name} was successfully edited! ")
    except BaseException:
        db.session.rollback()
        flash(f'An error occurred. Artist {artist.name} could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    # TODO: populate form with values from venue with ID <venue_id>
    venue_data = Venue.query.get(venue_id)
    form.name.default = venue_data.name
    form.city.default = venue_data.city
    form.state.default = venue_data.state
    form.address.default = venue_data.address
    form.phone.default = venue_data.phone
    form.genres.default = venue_data.genres
    form.website.default = venue_data.website
    form.facebook_link.default = venue_data.facebook_link
    form.image_link.default = venue_data.image_link
    form.seeking_talent.default = "Yes" if venue_data.seeking_talent else "No"
    form.seeking_description.default = venue_data.seeking_description
    form.process()
    return render_template(
        'forms/edit_venue.html',
        form=form,
        venue=venue_data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.website = request.form['website']
    venue.seeking_talent = True \
        if request.form['seeking_talent'] == 'Yes' else False
    venue.seeking_description = request.form['seeking_description']

    try:
        db.session.commit()
        flash(f"Venue {venue.name} was successfully edited! ")
    except BaseException:
        db.session.rollback()
        flash(f'An error occurred. Venue {venue.name} could not be listed.')
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
    # TODO: modify data to be the data object returned from db insertion
    try:
        artist_name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        facebook_link = request.form['facebook_link']
        image_link = request.form['image_link']
        website = request.form['website']
        seeking_venue = True \
            if request.form['seeking_venue'] == 'Yes' else False
        seeking_description = request.form['seeking_description']

        new_artist = Artist(
            name=artist_name,
            genres=genres,
            city=city,
            state=state,
            phone=phone,
            image_link=image_link,
            facebook_link=facebook_link,
            website=website,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description)

        db.session.add(new_artist)
        db.session.commit()
        flash(f"Artist {artist_name} was successfully listed! ")

    except BaseException:
        db.session.rollback()
        flash(f'An error occurred. Artist {artist_name} could not be listed.')
        # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be
    # listed.')
    finally:
        db.session.close()

    # on successful db insert, flash success

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per
    # venue.
    data = []
    shows = Show.query.all()
    for show in shows:
        temp_dict = {}
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        temp_dict['venue_id'] = venue.id
        temp_dict['venue_name'] = venue.name
        temp_dict['artist_id'] = artist.id
        temp_dict['artist_name'] = artist.name
        temp_dict['artist_image_link'] = artist.image_link
        temp_dict['start_time'] = show.start_time
        data.append(temp_dict)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing
    # form
    # TODO: insert form data as a new Show record in the db, instead

    try:

        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']
        new_show = Show(artist_id=artist_id, venue_id=venue_id,
                        start_time=start_time)
        db.session.add(new_show)
        db.session.commit()
        flash(f"Show was successfully listed! ")

    except BaseException:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        flash(f'An error occurred. New show could not be listed.')

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
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
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
