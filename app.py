from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String
from sqlalchemy.sql.sqltypes import Float, Integer
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import os


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'secret-key' 

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print("Database created successfully")

@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print("Database dropped!")

@app.cli.command('db_seed')
def db_seed():

    mercury = Planet(planet_name="Mercury", planet_type="Class A", home_star="Sol", mass=3.258e23, radius=1516, distance=35.98e6)
    venus = Planet(planet_name="Venus", planet_type="Class E", home_star="Sol", mass=4.867e24, radius=3760, distance=67.24e6)
    earth = Planet(planet_name="Earth", planet_type="Class K", home_star="Sol", mass=5.972e24, radius=3959, distance=92.96e6)
    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(first_name="John", last_name="Doe", email="john.doe@example.com", password="123456")
    db.session.add(test_user)

    db.session.commit()
    print("Database seeded")


# routes
@app.route("/")
def home():
    return jsonify(message="Hello from Planetary!")

@app.route("/planets", methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)

@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message="Email already exists"), 409
    
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    password = request.form["password"]
    user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify(message="User added to database")

@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        email = request.json["email"]
        password = request.json["password"]
    else:
        email = request.form["email"]
        password = request.form["password"]
    
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login successful", access_token=access_token)
    else:
        return jsonify(message="Incorrect email or password"), 401

@app.route("/planet_details/<int:planet_id>")
def planet_details(planet_id : int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(message="planet found!", planet_details=result)
    else:
        return jsonify(message="Planet does not exist")

@app.route("/add_planet", methods=["POST"])
@jwt_required()
def add_planet():

    planet_name = request.form["planet_name"]
    
    test = Planet.query.filter_by(planet_name=planet_name).first()
    if test:
        return jsonify(message="Planet name already exists"), 409

    planet_type = request.form["planet_type"]
    home_star = request.form["home_star"]
    mass = float(request.form["mass"])
    radius = float(request.form["radius"])
    distance = float(request.form["distance"])

    planet = Planet(planet_name=planet_name, planet_type=planet_type, home_star=home_star, mass=mass, radius=radius, distance=distance)
    db.session.add(planet)
    db.session.commit()

    return jsonify(message="Planet added successfully")

@app.route("/update_planet", methods=["PUT"])
@jwt_required()
def update_planet():
    planet_id = request.form["planet_id"]
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        planet.planet_name = request.form["planet_name"]
        planet.planet_type = request.form["planet_type"]
        planet.home_star = request.form["home_star"]
        planet.mass = float(request.form["mass"])
        planet.radius = float(request.form["radius"])
        planet.distance = float(request.form["distance"])
        db.session.commit()

        return jsonify(message="Planet updated successfully")
    else:
        return jsonify(message="Could not find planet")

@app.route("/delete_planet/<int:planet_id>", methods=["DELETE"])
@jwt_required()
def delete_planet(planet_id : str):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        
        return jsonify(message="Planet removed successfully")
    else:
        return jsonify(message="Could not find planet")


# database models
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


# db schemas - marshmallow
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')

class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_star', 'mass', 'radius', 'distance')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)


if __name__ == "__main__":
    app.run()