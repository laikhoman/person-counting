from builtins import staticmethod
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from sqlalchemy.ext.hybrid import hybrid_property
import math

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    places = db.relationship('Place', backref='user', lazy='dynamic')

    def __repr__(self):
        return "<User %r>" % self.name

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_password_hash(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Place(db.Model):
    __tablename__ = 'places'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    city = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cctvs = db.relationship('Cctv', backref='place', lazy='dynamic')

    def __repr__(self):
        return "<Place %r>" % self.name

class Cctv(db.Model):
    __tablename__ = 'cctvs'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64))
    url = db.Column(db.Text())
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'), nullable=False)
    lines = db.relationship('Line', backref='cctv', lazy='dynamic')

    def __repr__(self):
        return "<Cctv %r>" % self.label

class Line(db.Model):
    __tablename__ = 'lines'
    id = db.Column(db.Integer, primary_key=True)
    cctv_id = db.Column(db.Integer, db.ForeignKey('cctvs.id'), nullable=False)
    x1 = db.Column(db.Integer)
    y1 = db.Column(db.Integer)
    x2 = db.Column(db.Integer)
    y2 = db.Column(db.Integer)
    events = db.relationship('Event', backref='line', lazy='dynamic')

    def __repr__(self):
        return "<Line %r>" % str(self.id)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=True)
    event = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return "<Event %r>" % str(self.id)

    @staticmethod
    def _extract_quarter_hour(minute):
        # Rounds down to nearest quarter, alternatively
        # floor(minute / 15) * 15
        # return minute - minute % 15
        print("minute",minute)
        return minute - minute % 15

    @hybrid_property
    def quarter(self):
        return self._extract_quarter_hour(self.timestamp.minute)

    @quarter.expression
    def quarter(cls):
        minute = db.func.extract('minute', cls.timestamp).cast(db.Integer)
        return cls._extract_quarter_hour(minute)

    @hybrid_property
    def hour(self):
        return self.timestamp.hour

    @hour.expression
    def hour(cls):
        return db.func.extract('hour', cls.timestamp).cast(db.Integer)