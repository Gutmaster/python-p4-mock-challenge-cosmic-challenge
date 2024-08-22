#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = Scientist.query.all()
        return [{'id': scientist.id, 
                 'name': scientist.name, 
                 'field_of_study': scientist.field_of_study} for scientist in scientists], 200
    
    def post(self):
        data = request.json
        try:
            scientist = Scientist(name=data['name'], field_of_study=data['field_of_study'])
        except ValueError:
            return make_response({'errors': ['validation errors']}, 400)
        
        db.session.add(scientist)
        db.session.commit()
        return make_response(scientist.to_dict(), 201)

class ScientistsById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist is not None:
            return make_response(scientist.to_dict(), 200)
        else:
            return make_response({'error': 'Scientist not found'}, 404)
        
    def patch(self, id):
        data = request.json
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist is not None:
            try:
                scientist.name = data.get('name', scientist.name)
                scientist.field_of_study = data.get('field_of_study', scientist.field_of_study)
            except ValueError:
                return make_response({'errors': ['validation errors']}, 400)
            
            db.session.commit()
            return make_response(scientist.to_dict(), 202)
        else:
            return make_response({'error': 'Scientist not found'}, 404)
        
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist is not None:
            db.session.delete(scientist)
            db.session.commit()
            return make_response({}, 204)
        else:
            return make_response({'error': 'Scientist not found'}, 404)
    
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist is not None:
            db.session.delete(scientist)
            db.session.commit()
            return make_response({}, 204)
        else:
            return make_response({'error': 'Scientist not found'}, 404)
    
class Planets(Resource):
    def get(self):
        planets = Planet.query.all()
        return [{'id': planet.id, 
                 'name': planet.name, 
                 'distance_from_earth': planet.distance_from_earth, 
                 'nearest_star': planet.nearest_star} for planet in planets], 200
    
class Missions(Resource):
    def post(self):
        data = request.json
        try:
            scientist = Scientist.query.filter_by(id=data['scientist_id']).first()
            planet = Planet.query.filter_by(id=data['planet_id']).first()
            if scientist is None or planet is None:
                raise ValueError('Scientist or planet not found')
            
            mission = Mission(name=data['name'], scientist_id=scientist.id, planet_id=planet.id)
        except ValueError:
            return make_response({'errors': ['validation errors']}, 400)
        
        db.session.add(mission)
        db.session.commit()
        return make_response(mission.to_dict(), 201)

api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistsById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
