"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Person, Planet, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def get_all_people():
    people = Person.query.all()
    all_people = list(map(lambda x: x.serialize(), people))
    return jsonify(all_people), 200

@app.route('/people', methods=['POST'])
def add_person():
    data = request.get_json()
    person = Person(name=data['name'])
    db.session.add(person)
    db.session.commit()
    return 'Success', 200

@app.route('/people/<int:person_id>', methods=['GET'])
def get_person(person_id):
    person = Person.query.get(person_id)
    if person:
        return jsonify(person.serialize()), 200
    else:
        return "Person not found", 404
    
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planet = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), planet))
    return jsonify(all_planets), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
    else:
        return "Planet obliviated", 404

@app.route('/users', methods=['GET'])
def get_all_users():
    user = User.query.all()
    all_users = list(map(lambda x: x.serialize(), user))
    return jsonify(all_users), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    user = User.query.get(user_id)
    fav_planets = list(map(lambda x: x.serialize(), user.fav_planets)) if user.fav_planets else []
    fav_people = list(map(lambda x: x.serialize(), user.fav_people)) if user.fav_people else []
    favorites = fav_people + fav_planets
    return jsonify(favorites), 200

""" @app.route('/favorites/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    data = request.get_json()
    favorite = Favorites(user_id=data[user_id], fav_planets=data[planet_id])
    db.session.add(favorite)
    db.session.commit()
    return 'Favorite added', 200 """
    

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    person = Person(name=data['name'])
    db.session.add(person)
    db.session.commit()
    return 'Success', 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)