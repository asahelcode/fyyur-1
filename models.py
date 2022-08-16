from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY, TIMESTAMP

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

db = SQLAlchemy()

class Show(db.Model):
   __tablename__ = "shows"

   id = db.Column( db.Integer, primary_key=True)
   artist_id = db.Column(db.ForeignKey('artists.id'))
   venue_id = db.Column(db.ForeignKey('venues.id'))
   start_time = db.Column(TIMESTAMP(timezone=True))
   artists = db.relationship('Artist', lazy=False, back_populates='venues', uselist=False)
   venues = db.relationship('Venue', lazy=False, back_populates='artists', uselist=False)

   def __repr__(self):
    return f'<Show artist_id={self.artist_id}, venue_id={self.venue_id}>'

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String())
    genres = db.Column(ARRAY(db.String(120)))
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    websitelink =db.Column(db.String())
    seeking_talent=db.Column(db.BOOLEAN)
    seeking_description =db.Column(db.String())
    artists = db.relationship('Show', lazy=False, back_populates='venues', cascade='delete')

    def __repr__(self): # To aid my debugging
        return f'<Venue name={self.name} genres={self.genres}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable =False)
    state = db.Column(db.String(120))
    phone = db.Column(db.String())
    genres = db.Column(ARRAY(db.String(120)))
    image_link = db.Column(db.String())
    websitelink = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    seeking_venue=db.Column(db.BOOLEAN)
    seeking_description =db.Column(db.String())
    venues = db.relationship('Show', lazy=False, back_populates='artists')

    def __repr__(self): # To aid my debugging
        return f'<Artist name={self.name} genres={self.genres}>'
