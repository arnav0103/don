from Tool import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


work = db.Table('work',
                db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                db.Column('team_id', db.Integer, db.ForeignKey('teams.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    username = db.Column(db.String, unique=True)
    profile_image = db.Column(
        db.String(64), nullable=False, default='head_res.png')
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    master = db.Column(db.Integer, default=1)
    role = db.Column(db.Integer, default=0)

    application = db.relationship(
        'Application', backref='user', lazy='dynamic')
    knowledge = db.relationship('Knowledge', backref='user', lazy='dynamic')
    knowledge = db.relationship('Knowledge', backref='user', lazy='dynamic')
    teams = db.relationship('Team', secondary=work,
                            backref=db.backref('workers', lazy='dynamic'))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, name, username, email, password):
        self.email = email
        self.name = name
        self.username = username
        self.password_hash = generate_password_hash(password)


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    team_image = db.Column(db.String(64), nullable=False,
                           default='head_res.png')
    password_hash = db.Column(db.String(128))
    randomid = db.Column(db.String, unique=True)
    ownerid = db.Column(db.Integer)

    knowledge = db.relationship('Knowledge', backref='team', lazy='dynamic')
    events = db.relationship('Events', backref='team', lazy='dynamic')
    chats = db.relationship('Chat', backref='team', lazy='dynamic')

    def __init__(self, name, password, randomid,  ownerid):
        self.name = name
        self.password_hash = generate_password_hash(password)
        self.randomid = randomid
        self.ownerid = ownerid

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    message = db.Column(db.String)

    teamid = db.Column(db.Integer, db.ForeignKey('teams.id'))

    def __init__(self, name, message, teamid):
        self.name = name
        self.message = message
        self.teamid = teamid


class Events(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    teamid = db.Column(db.Integer, db.ForeignKey('teams.randomid'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    title = db.Column(db.String)
    event = db.Column(db.String)
    type = db.Column(db.String)

    def __init__(self, teamid, title, event, type):
        self.teamid = teamid
        self.title = title
        self.event = event
        self.type = type


class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    body = db.Column(db.Integer)
    criminal = db.Column(db.String)
    years = db.Column(db.Integer)
    connection = db.Column(db.String)
    image = db.Column(db.String(64), nullable=False)
    rented = db.Column(db.String, default='No')

    userid = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, body, criminal, userid, years, connection, image):
        self.name = name
        self.body = body
        self.criminal = criminal
        self.userid = userid
        self.years = years
        self.connection = connection
        self.image = image


class Knowledge(db.Model):
    __tablename__ = 'knowledge'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    title = db.Column(db.String)
    content = db.Column(db.String)
    image = db.Column(db.String(64), nullable=True)

    teamid = db.Column(db.Integer, db.ForeignKey('teams.id'))
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, title, content, teamid, userid):
        self.title = title
        self.content = content
        self.teamid = teamid
        self.userid = userid

# inventory models


class Car(db.Model):
    __tablename__ = 'car'
    id = db.Column(db.Integer, primary_key=True)
    car = db.Column(db.Integer, nullable=True)
    truck = db.Column(db.Integer, nullable=True)
    helicopter = db.Column(db.Integer, nullable=True)
    date = db.Column(db.DateTime, nullable=True)

    def __init__(self, car, truck, helicopter, date):
        self.car = car
        self.truck = truck
        self.helicopter = helicopter
        self.date = date
