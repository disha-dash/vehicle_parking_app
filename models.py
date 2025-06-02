from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(80), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(35), nullable=False, default='user')
    reserve = db.relationship('Reserve_Parking_Spot', backref='user')

class Parking_Lot(db.Model):
    __tablename__ = 'parking_lots'

    lot_id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    spot = db.relationship('Parking_Spot', backref='lot')

class Spot_status(enum.Enum):
    vacant = "Vacant"
    occupied = "Occupied"

class Parking_Spot(db.Model):
    __tablename__ = 'parking_spots'

    spot_id = db.Column(db.Integer, primary_key=True)
    spot_no = db.Column(db.Integer, nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.lot_id'), nullable=False)
    status = db.Column(db.Enum(Spot_status), nullable=False, default=Spot_status.vacant)
    reserved = db.relationship('Reserve_Parking_Spot', backref='spot')
    
class Reserve_Parking_Spot(db.Model):
    __tablename__ = 'reserve_parking_spots'

    reserve_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), db.ForeignKey('users.user_id'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.lot_id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.spot_id'), nullable=False)
    status = db.Column(db.Enum(Spot_status), nullable=False, default=Spot_status.vacant)
    parking_time = db.Column(db.DateTime, server_default=db.func.now(), nullable=True)
    leaving_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, nullable=True)
    cost = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    lot = db.relationship('Parking_Lot', backref='reservations')