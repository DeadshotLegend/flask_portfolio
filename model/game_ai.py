""" database dependencies to support sqliteDB examples """
from random import randrange
from datetime import date
import os, base64
import json
from flask import jsonify
from __init__ import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


''' Tutorial: https://www.sqlalchemy.org/library.html#tutorials, try to get into Python shell and follow along '''

# Define the Post class to manage actions in 'posts' table,  with a relationship to 'users' table
class Games(db.Model):
    __tablename__ = 'games'

    # Define the Games schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=False, nullable=False)
    win = db.Column(db.String, unique=False)
    kills = db.Column(db.Integer, unique=False)
    deaths = db.Column(db.Integer, unique=False)
    playdatetime = db.Column(db.Date, unique=False, nullable=False)
    # Define a relationship in Games Schema to userID who played the game, many-to-one (many games to one user)
    userID = db.Column(db.Integer, db.ForeignKey('gamers.id'))

    # Constructor of a Notes object, initializes of instance variables within object
    def __init__(self, id, name, win, kills, deaths, playdatetime):
        self.userID = id
        self.name = name
        self.win = win
        self.kills = kills
        self.deaths = deaths
        self.playdatetime = playdatetime

    # Returns a string representation of the Game object, similar to java toString()
    # returns string
    def __repr__(self):
        return "Game(" + str(self.id) + "," + self.name + "," + str(self.userID)+ "," + str(self.win)+ "," + str(self.kills)+ "," + str(self.deaths)+ "," + str(self.playdatetime) + ")"

    # CRUD create, adds a new record to the Games table
    # returns the object added or None in case of an error
    def create(self):
        try:
            # creates a Games object from Games(db.Model) class, passes initializers
            db.session.add(self)  # add prepares to persist person object to Games table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.remove()
            return None

    # CRUD read, returns dictionary representation of Notes object
    # returns dictionary
    def read(self):
        return {
            "id": self.id,
            "userID": self.userID,
            "name": self.name,
            "win": self.win,
            "kills": self.kills,
            "deaths": self.deaths,
            "playdatetime": self.playdatetime
        }


# Define the User class to manage actions in the 'gamers' table
# -- Object Relational Mapping (ORM) is the key concept of SQLAlchemy
# -- a.) db.Model is like an inner layer of the onion in ORM
# -- b.) User represents data we want to store, something that is built on db.Model
# -- c.) SQLAlchemy ORM is layer on top of SQLAlchemy Core, then SQLAlchemy engine, SQL
class Gamer(db.Model):
    __tablename__ = 'gamers'  # table name is plural, class name is singular

    # Define the Gamer schema with "vars" from object
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=False, nullable=False)
    _uid = db.Column(db.String(255), unique=True, nullable=False)
    _password = db.Column(db.String(255), unique=False, nullable=False)
    _dob = db.Column(db.Date)

    # Defines a relationship between gamer record and games table, one-to-many (one user to many games)
    games = db.relationship("Games", cascade='all, delete', backref='gamers', lazy=True)

    # constructor of a Gamer object, initializes the instance variables within object (self)
    def __init__(self, name, uid, password="123qwerty", dob=date.today()):
        self._name = name    # variables with self prefix become part of the object, 
        self._uid = uid
        self.set_password(password)
        self._dob = dob

    # a name getter method, extracts name from object
    @property
    def name(self):
        return self._name
    
    # a setter function, allows name to be updated after initial object creation
    @name.setter
    def name(self, name):
        self._name = name
    
    # a getter method, extracts email from object
    @property
    def uid(self):
        return self._uid
    
    # a setter function, allows name to be updated after initial object creation
    @uid.setter
    def uid(self, uid):
        self._uid = uid
        
    # check if uid parameter matches user id in object, return boolean
    def is_uid(self, uid):
        return self._uid == uid
    
    @property
    def password(self):
        return self._password[0:10] + "..." # because of security only show 1st characters

    # update password, this is conventional setter
    def set_password(self, password):
        """Create a hashed password."""
        self._password = generate_password_hash(password, method='sha256')

    # check password parameter versus stored/encrypted password
    def is_password(self, password):
        """Check against hashed password."""
        result = check_password_hash(self._password, password)
        return result
    
    # dob property is returned as string, to avoid unfriendly outcomes
    @property
    def dob(self):
        dob_string = self._dob.strftime('%m-%d-%Y')
        return dob_string
    
    # dob should be have verification for type date
    @dob.setter
    def dob(self, dob):
        self._dob = dob
    
    @property
    def age(self):
        today = date.today()
        return today.year - self._dob.year - ((today.month, today.day) < (self._dob.month, self._dob.day))
    
    # output content using str(object) in human readable form, uses getter
    # output content using json dumps, this is ready for API response
    def __str__(self):
        return json.dumps(self.read())

    # CRUD create/add a new record to the table
    # returns self or None on error
    def create(self):
        try:
            print("Creating gamer:" + self.name)
            # creates a person object from Gamer(db.Model) class, passes initializers
            db.session.add(self)  # add prepares to persist person object to Gamers table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            print("--Created gamer: " + self.name)
            return self
        except IntegrityError as err:
            print("Exception in creating gamer" + self.name)
            print(err)
            db.session.remove()
            return None

    # CRUD read converts self to dictionary
    # returns dictionary
    def read(self):
        return {
            "id": self.id,
            "name": self.name,
            "uid": self.uid,
            "dob": self.dob,
            "age": self.age,
            "games": [game.read() for game in self.games]
        }

    # CRUD update: updates user name, password, phone
    # returns self
    def update(self, name="", uid="", password=""):
        """only updates values with length"""
        if len(name) > 0:
            self.name = name
        if len(uid) > 0:
            self.uid = uid
        if len(password) > 0:
            self.set_password(password)
        db.session.commit()
        return self

    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


"""Database Creation and Testing """


# Builds working data for testing
def initGamers():
    print("Creating gamers")
    """Create database and tables"""
    app.app_context().push()
    db.create_all()
    """Tester data for table"""
    u1 = Gamer(name='Thomas Edison', uid='toby', password='123toby', dob=date(1847, 2, 11))
    u2 = Gamer(name='Nicholas Tesla', uid='niko', password='123niko')
    u3 = Gamer(name='Alexander Graham Bell', uid='lex', password='123lex')
    u4 = Gamer(name='Eli Whitney', uid='whit', password='123whit')
    u5 = Gamer(name='John Mortensen', uid='jm1021', dob=date(1959, 10, 21))

    gamers = [u1, u2, u3, u4, u5]

    """Builds sample gamer/game(s) data"""
    for gamer in gamers:
        try:
            '''add a few 1 to 4 notes per gamer'''
            for num in range(randrange(1, 4)):
                gamer.games.append(Games(id=gamer.id, name="Apex", win="Yes", kills=1, deaths=2, playdatetime=date.today()))
            '''add user/post data to table'''
            gamer = gamer.create()
            #print(jsonify(gamer.read()))
        except IntegrityError:
            '''fails with bad or duplicate data'''
            db.session.remove()
            print(f"Records exist, duplicate email, or error: {gamer.uid}")

#initGamers()