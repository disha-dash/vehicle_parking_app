from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class User(db.Model):
    
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(35), nullable=False)
    reserved = db.relationship('Reserve_Parking_Lot', backref='user')

    
class Parking_Lot(db.Model):
    __tablename__ = 'parking_lots'

    lot_id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120), nullable=False)
    pin_code = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    spot = db.relationship('Parking_Spot', backref='lot')

class Spot_status(enum.Enum):
    vacant = "Vacant"
    occupied = "Occupied"

class Parking_Spot(db.Model):
    __tablename__ = 'parking_spots'

    spot_id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.lot_id'), nullable=False)
    status = db.Column(db.Enum(Spot_status), nullable=False, default=Spot_status.vacant)
    reserve = db.relationship('Reserve_Parking_Spot', backref='spot', uselist=False)
    
class Reserve_Parking_Spot(db.Model):
    __tablename__ = 'reserve_parking_spots'

    reserve_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.spot_id'), nullable=False, unique=True)
    parking_time = db.Column(db.DateTime, server_default=db.func.now())
    leaving_time = db.Column(db.DateTime, nullable=True)
    cost = db.Column(db.Float, nullable=False)