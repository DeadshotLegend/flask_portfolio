from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime
from datetime import date

from model.game_ai import Gamer, Games

gamer_api = Blueprint('gamer_api', __name__,
                   url_prefix='/api/gamers')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(gamer_api)

class GamerAPI:        
    class _Create(Resource):
        def post(self):
            ''' Read data for json body '''
            body = request.get_json()
            
            ''' Avoid garbage in, error checking '''
            # validate name
            name = body.get('name')
            if name is None or len(name) < 2:
                return {'message': f'Name is missing, or is less than 2 characters'}, 210
            # validate uid
            uid = body.get('uid')
            if uid is None or len(uid) < 2:
                return {'message': f'User ID is missing, or is less than 2 characters'}, 210
            # look for password and dob
            password = body.get('password')
            dob = body.get('dob')

            ''' #1: Key code block, setup USER OBJECT '''
            uo = Gamer(name=name, 
                      uid=uid)
            
            ''' Additional garbage error checking '''
            # set password if provided
            if password is not None:
                uo.set_password(password)
            # convert to date type
            if dob is not None:
                try:
                    uo.dob = datetime.strptime(dob, '%m-%d-%Y').date()
                except:
                    return {'message': f'Date of birth format error {dob}, must be mm-dd-yyyy'}, 210
            
            for games in body.get('games'):
              gameo = Games(id=games.get('userID'), name=games.get('name'),
               win=games.get('win'), 
               kills=games.get('kills'), 
               deaths=games.get('deaths'), playdatetime=date.today() )
              uo.games.append(gameo)

            ''' #2: Key Code block to add user to database '''
            # create user in database
            gamer = uo.create()
            # success returns json of user
            if gamer:
                return jsonify(gamer.read())
            # failure returns error
            return {'message': f'Processed {name}, either a format error or User ID {uid} is duplicate'}, 210

    class _Read(Resource):
        def get(self):
            gamers = Gamer.query.all()    # read/extract all users from database
            json_ready = [gamer.read() for gamer in gamers]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps

    # building RESTapi endpoint
    api.add_resource(_Create, '/create')
    api.add_resource(_Read, '/')