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
from models import db, User, Planet, Favorite, Vehicle, Character
from sqlalchemy import and_
from models import db, User, Planet, Favorite, Vehicle, Character
from sqlalchemy import and_
#se me dificulto el commit y le puse otro nombre, esta linea es para poder cambiarle el nombre al commit
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

#endpoints
#crear user
@app.route('/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        existing_user = User.query.filter_by(email=data["email"]).first()
        
        if existing_user:
            return jsonify({"msg": "Email already exists"}), 400

        user_created = User(name=data["name"], email=data["email"], password=data["password"], is_active=data["is_active"])
        db.session.add(user_created)
        db.session.commit()
        response_body = {
            "msg": "User created successfully",
        }
        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
#get all users
@app.route('/user', methods=['GET'])
def get_users():
    try:
        results_query = User.query.all()
        results = list(map(lambda item: item.serialize(), results_query))
        response_body = {
            "msg": "Ok",
            "results": results
        }
        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    
#get user by id
@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    try:
        results_query = User.query.filter_by(id=id).first()
        if results_query:
            response_body = {
            "msg": "Ok",
            "results": results_query.serialize()
            }
            return jsonify(response_body), 200
        return jsonify({"msg": "No existe ese usuario"}), 400
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

#DELETE user
@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if user:
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"msg": "User deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()  
            return jsonify({"msg": str(e)}), 500
    else:
        return jsonify({"msg": "User not found"}), 404

#update user
@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)

    if user:
        data = request.get_json()

        # Actualiza los campos del usuario
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.password = data['password']  # Mejorar la seguridad para crear contraseña
        if 'is_active' in data:
            user.is_active = data['is_active']

        try:
            db.session.commit()
            return jsonify({"msg": "Usuario actualizado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": f"Error al actualizar: {str(e)}"}), 500
    else:
        return jsonify({"msg": "Usuario no encontrado"}), 404
#get all planets
@app.route('/planet', methods=['GET'])
def get_planets():
    try:
        results_query = Planet.query.all()
        results = list(map(lambda item: item.serialize(), results_query))
        if results_query:
            response_body = {
            "msg": "Ok",
            "results": results
            }
            return jsonify(response_body), 200
        return jsonify({"msg": "No hay planetas"}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
#get Planet by planet_id
@app.route('/planet/<int:id>', methods=['GET'])
def get_planet(id):
    try:
        results_query = Planet.query.filter_by(id=id).first()
        if results_query:
            response_body = {
            "msg": "Ok",
            "results": results_query.serialize()
            }
            return jsonify(response_body), 200
        return jsonify({"msg": "No existe ese planeta"}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500 
#DELETE PLANET by id
@app.route('/planet/<int:id>', methods=['DELETE'])
def delete_planet(id):
    planet = Planet.query.get(id)
    if planet:
        try:
            db.session.delete(planet)
            db.session.commit()
            return jsonify({"msg": "Planeta eliminado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": f"Error al eliminar el planeta: {str(e)}"}), 500
    else:
        return jsonify({"msg": "Planeta no encontrado"}), 404
#UPDATE PLANET
@app.route('/planet/<int:id>', methods=['PUT'])
def update_planet(id):
    planet = Planet.query.get(id)
    if planet:
        data = request.get_json()

        # Actualiza los campos del planeta
        if 'climate' in data:
            planet.climate = data['climate']
        if 'diameter' in data:
            planet.diameter = data['diameter']
        if 'gravity' in data:
            planet.gravity = data['gravity']
        if 'like' in data:
            planet.like = data['like']
        if 'name' in data:
            planet.name = data['name']
        if 'orbital_period' in data:
            planet.orbital_period = data['orbital_period']
        if 'population' in data:
            planet.population = data['population']
        if 'rotation_period' in data:
            planet.rotation_period = data['rotation_period']
        if 'surface_water' in data:
            planet.surface_water = data['surface_water']
        if 'terrain' in data:
            planet.terrain = data['terrain']

        try:
            db.session.commit()
            return jsonify({"msg": "Planeta actualizado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": f"Error al actualizar el planeta: {str(e)}"}), 500
    else:
        return jsonify({"msg": "Planeta no encontrado"}), 404

#get Characters
@app.route('/character', methods=['GET'])
def get_characters():
    try:
        results_query = Character.query.all()
        results = list(map(lambda item: item.serialize(), results_query))
        response_body = {
            "msg": "Ok",
            "results": results
        }
        if results_query:
            return jsonify(response_body), 200
        return jsonify({"msg": "No existen personajes"}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
#GET CHARACTER BY ID
@app.route('/character/<int:id>', methods=['GET'])
def get_character(id):
    try:
        results_query = Character.query.filter_by(id=id).first()
        if results_query: 
            response_body = {
                "msg": "Ok",
                "results": results_query.serialize()
            }
            return jsonify(response_body), 200
        return jsonify({"msg": "Personaje no encontrado"}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
#delete character
@app.route('/character/<int:id>', methods=['DELETE'])
def delete_character(id):
    character = Character.query.get(id)
    if character:
        try:
            db.session.delete(character)
            db.session.commit()
            return jsonify({"msg": "Personaje eliminado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": f"Error al eliminar el personaje: {str(e)}"}), 500
    else:
        return jsonify({"msg": "Personaje no encontrado"}), 404
#UPDATE CHARACTER
@app.route('/character/<int:id>', methods=['PUT'])
def update_character(id):
    character = Character.query.get(id)
    if character:
        data = request.get_json()

        # Actualiza los campos del personaje
        if 'name' in data:
            character.name = data['name']
        if 'height' in data:
            character.height = data['height']
        if 'mass' in data:
            character.mass = data['mass']
        if 'hair_color' in data:
            character.hair_color = data['hair_color']
        if 'skin_color' in data:
            character.skin_color = data['skin_color']
        if 'eye_color' in data:
            character.eye_color = data['eye_color']
        if 'birth_year' in data:
            character.birth_year = data['birth_year']
        if 'gender' in data:
            character.gender = data['gender']

        try:
            db.session.commit()
            return jsonify({"msg": "Personaje actualizado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": f"Error al actualizar el personaje: {str(e)}"}), 500
    else:
        return jsonify({"msg": "Personaje no encontrado"}), 404
#Obtener Todos los Vehículos
@app.route('/vehicle', methods=['GET'])
def get_vehicles():
    try:
        results_query = Vehicle.query.all()
        results = list(map(lambda item: item.serialize(), results_query))
        response_body = {
            "msg": "Ok",
            "results": results
        }
        if results_query:
            return jsonify(response_body), 200
        return jsonify({"msg": "No existen vehículos"}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
#Obtener Vehículo por ID
@app.route('/vehicle/<int:id>', methods=['GET'])
def get_vehicle(id):
    try:
        results_query = Vehicle.query.filter_by(id=id).first()
        if results_query:
            response_body = {
                "msg": "Ok",
                "results": results_query.serialize()
            }
            return jsonify(response_body), 200
        return jsonify({"msg": "Vehículo no encontrado"}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
#Eliminar Vehículo
@app.route('/vehicle/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    vehicle = Vehicle.query.get(id)
    if vehicle:
        try:
            db.session.delete(vehicle)
            db.session.commit()
            return jsonify({"msg": "Vehículo eliminado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": f"Error al eliminar el vehículo: {str(e)}"}), 500
    else:
        return jsonify({"msg": "Vehículo no encontrado"}), 404
#Actualizar Vehículo
@app.route('/vehicle/<int:id>', methods=['PUT'])
def update_vehicle(id):
    vehicle = Vehicle.query.get(id)
    if vehicle:
        data = request.get_json()

        # Actualiza los campos del vehículo
        if 'name' in data:
            vehicle.name = data['name']
        if 'model' in data:
            vehicle.model = data['model']
        if 'manufacturer' in data:
            vehicle.manufacturer = data['manufacturer']
        if 'cost_in_credits' in data:
            vehicle.cost_in_credits = data['cost_in_credits']
        if 'length' in data:
            vehicle.length = data['length']
        if 'max_atmosphering_speed' in data:
            vehicle.max_atmosphering_speed = data['max_atmosphering_speed']
        if 'crew' in data:
            vehicle.crew = data['crew']
        if 'passengers' in data:
            vehicle.passengers = data['passengers']
        if 'cargo_capacity' in data:
            vehicle.cargo_capacity = data['cargo_capacity']
        if 'consumables' in data:
            vehicle.consumables = data['consumables']
        if 'vehicle_class' in data:
            vehicle.vehicle_class = data['vehicle_class']

        try:
            db.session.commit()
            return jsonify({"msg": "Vehículo actualizado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": f"Error al actualizar el vehículo: {str(e)}"}), 500
    else:
        return jsonify({"msg": "Vehículo no encontrado"}), 404
#GET FAVORITES BY USER ID
@app.route('/users/<int:id>/favorites', methods=['GET'])
def get_favorites(id):
    try:
        results_query = Favorite.query.filter_by(user_id=id).all()
        if results_query:
            results = list(map(lambda item: item.serialize(), results_query))
            response_body = {
                "msg": "Ok",
                "results": results
            }
            return jsonify(response_body), 200
        return jsonify({"msg": "No hay favoritos para este usuario."}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

#AGREGAR PLANETA FAVORITO
@app.route('/users/<int:user_id>/favorites/planet/<int:planet_id>', methods=['POST'])
def create_favorite_planet(user_id, planet_id):
    try:
        user_exists = User.query.filter_by(id=user_id).first()
        if not user_exists:
            return jsonify({"msg": "El usuario no existe"}), 400
        planet_exists = Planet.query.filter_by(id=planet_id).first()
        if not planet_exists:
            return jsonify({"msg": "El planeta no existe"}), 400
        existing_favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
        if existing_favorite:
            return jsonify({"msg": "El favorito ya existe"}), 400
        favorite_created = Favorite(user_id=user_id, planet_id=planet_id)
        db.session.add(favorite_created)
        db.session.commit()
        response_body = {
            "msg": "Favorito creado",
            "favorito": favorite_created.serialize()
        }
        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

#AGREGAR CHARACTER FAVORITO
@app.route('/users/<int:user_id>/favorites/character/<int:character_id>', methods=['POST'])
def create_favorite_character(user_id, character_id):
    try:
        user_exists = User.query.filter_by(id=user_id).first()
        if not user_exists:
            return jsonify({"msg": "El usuario no existe"}), 400
        character_exists = Character.query.filter_by(id=character_id).first()
        if not character_exists:
            return jsonify({"msg": "El character no existe"}), 400
        existing_favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
        if existing_favorite:
            return jsonify({"msg": "El favorito ya existe"}), 400
        favorite_created = Favorite(user_id=user_id, character_id=character_id)
        db.session.add(favorite_created)
        db.session.commit()
        response_body = {
            "msg": "Favorito creado",
            "favorito": favorite_created.serialize()
        }
        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
#AGREGAR VEHICLE FAVORITO
@app.route('/users/<int:user_id>/favorites/vehicle/<int:vehicle_id>', methods=['POST'])
def create_favorite_vehicle(user_id, vehicle_id):
    try:
        user_exists = User.query.filter_by(id=user_id).first()
        if not user_exists:
            return jsonify({"msg": "El usuario no existe"}), 400
        vehicle_exists = Vehicle.query.filter_by(id=vehicle_id).first()
        if not vehicle_exists:
            return jsonify({"msg": "El vehículo no existe"}), 400
        existing_favorite = Favorite.query.filter_by(user_id=user_id, vehicle_id=vehicle_id).first()
        if existing_favorite:
            return jsonify({"msg": "El favorito ya existe"}), 400
        favorite_created = Favorite(user_id=user_id, vehicle_id=vehicle_id)
        db.session.add(favorite_created)
        db.session.commit()
        response_body = {
            "msg": "Favorito creado",
            "favorito": favorite_created.serialize()
        }
        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    
#DELETE PLANET FROM FAVORITES
@app.route('/users/<int:user_id>/favorites/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    try:
        user_exists = User.query.filter_by(id=user_id).first()
        if not user_exists:
            return jsonify({"msg": "El usuario no existe"}), 400
        planet_exists = Planet.query.filter_by(id=planet_id).first()
        if not planet_exists:
            return jsonify({"msg": "El planeta no existe"}), 400
        existing_favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
        if existing_favorite:
            db.session.delete(existing_favorite)
            db.session.commit()
            return jsonify({"msg": "El favorito fue eliminado"}), 200
        return jsonify({"msg": "No existe ese favorito, no se pudo eliminar"}), 400
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

#DELETE character FROM FAVORITES
@app.route('/users/<int:user_id>/favorites/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(user_id, character_id):
    try:
        user_exists = User.query.filter_by(id=user_id).first()
        if not user_exists:
            return jsonify({"msg": "El usuario no existe"}), 400
        character_exists = Character.query.filter_by(id=character_id).first()
        if not character_exists:
            return jsonify({"msg": "El character no existe"}), 400
        existing_favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
        if existing_favorite:
            db.session.delete(existing_favorite)
            db.session.commit()
            return jsonify({"msg": "El favorito fue eliminado"}), 200
        return jsonify({"msg": "Ese favorito no existe, no se pudo eliminar"}), 400
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
#DELETE veihcle FROM FAVORITES
@app.route('/users/<int:user_id>/favorites/vehicle/<int:vehicle_id>', methods=['DELETE'])
def delete_favorite_vehicle(user_id, vehicle_id):
    try:
        # Verificar si el usuario existe
        user_exists = User.query.filter_by(id=user_id).first()
        if not user_exists:
            return jsonify({"msg": "El usuario no existe"}), 400

        # Verificar si el vehículo existe
        vehicle_exists = Vehicle.query.filter_by(id=vehicle_id).first()
        if not vehicle_exists:
            return jsonify({"msg": "El vehículo no existe"}), 400

        # Verificar si el favorito existe
        existing_favorite = Favorite.query.filter_by(user_id=user_id, vehicle_id=vehicle_id).first()
        if existing_favorite:
            db.session.delete(existing_favorite)
            db.session.commit()
            return jsonify({"msg": "El favorito fue eliminado"}), 200

        return jsonify({"msg": "No existe ese favorito, no se pudo eliminar"}), 404

    except Exception as e:
        return jsonify({"msg": str(e)}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)