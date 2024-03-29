from flask import Flask, render_template, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import platform
import jwt

app = Flask(__name__)
CORS(app)

# DO NOT REMOVE
print(platform.system())
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+mysqlconnector://root:password@localhost:3306/techtrek24"

db = SQLAlchemy(app)


# generate a token based on unique username
def generate_username_token(username):
    msg = {"username": username}
    token = jwt.encode(msg, "secret", algorithm="HS256").decode("utf-8")
    return token


# decode token to check whether the user is logged in
def decode_token(token):
    decode_token = jwt.decode(token, "secret", algorithms=["HS256"])
    username = decode_token["username"]
    username_exist = User.query.filter_by(username=username).first()
    if username_exist:
        return True
    else:
        abort(401, description="Please login first.")


# check name is between 1-50 characters inclusive in length
def valid_name(name):
    if len(name) < 1:
        abort(401, description="Name cannot be empty.")
    elif len(name) > 50:
        abort(401, description="Please enter a name between 1-50 characters long.")
    else:
        return True


# check whether the username is already exist
def valid_username(username):
    username_exist = User.query.filter_by(username=username).first()
    if username_exist:
        abort(401, description="Username is already exist.")
    else:
        return True


# check password validation
def valid_password(password):
    if len(password) < 8:
        abort(401, description="Password should contain at least 6 characters.")
    elif len(password) > 20:
        abort(401, description="length should be not be greater than 20.")
    elif not any(char.isdigit() for char in password):
        abort(401, description="Password should have at least one numeral.")
    elif not any(char.isupper() for char in password):
        abort(401, description="Password should have at least one uppercase letter.")
    elif not any(char.islower() for char in password):
        abort(401, description="Password should have at least one lowercase letter.")
    else:
        return True


# generate hidden password
def generate_token(password):
    msg = {"password": password}
    token = jwt.encode(msg, "secret", algorithm="HS256").decode("utf-8")
    return token


# check password correction
def correct_password(username, password):
    user = User.query.filter_by(username=username).first()

    if user:
        correct_password = user.password
        if correct_password == password:
            return True
        else:
            abort(401, description="Wrong password.")
    else:
        abort(401, description="The username is not exist.")


class Country(db.Model):
    tablename = "country"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def json(self):
        return {"id": self.id, "name": self.name}


class Destination(db.Model):
    tablename = "destination"
    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey("country.id"), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def __init__(self, id, country_id, cost, name, notes):
        self.id = id
        self.country_id = country_id
        self.cost = cost
        self.name = name
        self.notes = notes

    def json(self):
        return {
            "id": self.id,
            "country_id": self.country_id,
            "cost": self.cost,
            "name": self.name,
            "notes": self.notes,
        }


class User(db.Model):
    tablename = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), nullable=False)

    def init(self, id, username, first_name, last_name, password):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.password = password

    def json(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "password": self.password,
            "username": self.username,
        }


class Itinerary(db.Model):
    tablename = "itinerary"
    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey("country.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    title = db.Column(db.String(100), nullable=False)

    def init(self, id, country_id, user_id, budget, title):
        self.id = id
        self.country_id = country_id
        self.user_id = user_id
        self.budget = budget
        self.title = title

    def json(self):
        return {
            "id": self.id,
            "country_id": self.country_id,
            "user_id": self.user_id,
            "budget": self.budget,
            "title": self.title,
        }


class ItineraryDestination(db.Model):
    tablename = "itinerary_destination"
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(
        db.Integer, db.ForeignKey("destination.id"), nullable=False
    )
    itinerary_id = db.Column(db.Integer, db.ForeignKey("itinerary.id"), nullable=False)

    def init(self, id, destination_id, itinerary_id):
        self.id = id
        self.destination_id = destination_id
        self.itinerary_id = itinerary_id

    def json(self):
        return {
            "id": self.id,
            "destination_id": self.destination_id,
            "itinerary_id": self.itinerary_id,
        }


# CREATE USER
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    password = data["password"]
    valid_name(data["first_name"])
    valid_name(data["last_name"])
    valid_username(data["username"])
    valid_password(password)
    hashed_password = generate_token(password)
    new_user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        username=data["username"],
        password=hashed_password,
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.json()), 201


# LOGIN
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    hashed_password = generate_token(data["password"])
    token = generate_username_token(data["username"])
    if correct_password(data["username"], hashed_password):
        return {"is_success": True, "token": token}
    else:
        return {"is_success": False}


# LOGOUT
@app.route("/auth/logout", methods=["POST"])
def logout():
    data = request.get_json()
    return {"is_success": True}


# USER DETAILS
@app.route("/<string:user_id>/details", methods=["GET"])
def dashboard(user_id):
    itinerary = Itinerary.query.filter_by(user_id=user_id)
    output = []
#    data = request.get_json()
#    token = data["token"]
#    decode_token(token)
    for i in itinerary:
        country = Country.query.filter_by(id=i.country_id).first().json()

        destinations = []
        itinerary_destination = ItineraryDestination.query.filter_by(itinerary_id=i.id)

    for id in itinerary_destination:
        destination = Destination.query.filter_by(id=id.destination_id).first()
        destinations.append(destination.json())
        output.append(
            {
                "title": i.title,
                "budget": i.budget,
                "country": country,
                "destinations": destinations,
            }
        )

    return output


@app.route("/countries", methods=["GET"])
def get_countries():
    output = []
    countries = Country.query.all()
    for c in countries:
        output.append(c.name)
    return output


# CREATE DESTINATION
@app.route("/destination", methods=["POST"])
def create_destination():
    data = request.get_json()
#    token = data["token"]
#    decode_token(token)
    destination = Destination(
        country_id=data["country_id"],
        cost=data["cost"],
        name=data["name"],
        notes=data["notes"],
    )
    try:
        db.session.add(destination)
        db.session.commit()
    except:
        return jsonify({"message": "An error occurred creating the destination."}), 500
    return jsonify(destination.json()), 201


# UPDATE DESTINATION
@app.route("/destination/<string:destination_id>", methods=["PUT"])
def update_destination(destination_id):
    destination = Destination.query.filter_by(id=destination_id).first()
    if destination:
        data = request.get_json()
#        token = data["token"]
#        decode_token(token)
        destination.country_id = data["country_id"]
        destination.cost = data["cost"]
        destination.name = data["name"]
        destination.notes = data["notes"]
        try:
            db.session.commit()
        except:
            return (
                jsonify({"message": "An error occurred updating the destination."}),
                500,
            )
        return jsonify(destination.json()), 200
    return jsonify({"message": "destination not found."}), 404


# DELETE DESTINATION
@app.route("/destination/<string:destination_id>", methods=["DELETE"])
def delete_destination(destination_id):
    destination = Destination.query.filter_by(id=destination_id).first()
    if destination:
#        data = request.get_json()
#        token = data["token"]
#        decode_token(token)
        try:
            db.session.delete(destination)
            db.session.commit()
        except:
            return (
                jsonify({"message": "An error occurred deleting the destination."}),
                500,
            )
        return jsonify({"message": "destination deleted."}), 200
    return jsonify({"message": "destination not found."}), 404


# CREATE ITINERARY
@app.route("/itinerary", methods=["POST"])
def create_itinerary():
    data = request.json
    new_itinerary = Itinerary(
        country_id=data["country_id"],
        user_id=data["user_id"],
        budget=data["budget"],
        title=data["title"],
    )

    try:
        db.session.add(new_itinerary)
        db.session.commit()
    except:
        return jsonify({"message": "An error occurred creating the itinerary."}), 500
    
    itinerary_details = {
        "id": new_itinerary.id,
        "country_id": new_itinerary.country_id,
        "user_id": new_itinerary.user_id,
        "budget": new_itinerary.budget,
        "title": new_itinerary.title,
    }

    return jsonify({"message": "Itinerary created successfully", "itinerary_details": itinerary_details}), 201


# GET ALL ITINERARIES
@app.route("/itinerary", methods=["GET"])
def get_itineraries():
    itineraries = Itinerary.query.all()
    return jsonify([itinerary.json() for itinerary in itineraries])


# GET 1 ITINERARY BASED ON ITINERARY_ID
@app.route("/itinerary/<itinerary_id>", methods=["GET"])
def get_itinerary(itinerary_id):
    itinerary = Itinerary.query.get(itinerary_id)
    if itinerary:
        return jsonify(itinerary.json())
    else:
        return jsonify({"message": "Itinerary not found"}), 404


# UPDATE ITINERARY BASED ON ITINERARY_ID
@app.route("/itinerary/<itinerary_id>", methods=["PUT"])
def update_itinerary(itinerary_id):
    itinerary = Itinerary.query.get(itinerary_id)
    if itinerary:
        data = request.json
        itinerary.country_id = data["country_id"]
        itinerary.user_id = data["user_id"]
        itinerary.budget = data["budget"]
        itinerary.title = data["title"]
        db.session.commit()
        return jsonify(itinerary.json())
    else:
        return jsonify({"message": "Itinerary not found"}), 404


# DELETE ITINERARY BASED ON ITINERARY_ID
@app.route("/itinerary/<itinerary_id>", methods=["DELETE"])
def delete_itinerary(itinerary_id):
    itinerary = Itinerary.query.get(itinerary_id)
    if itinerary:
        db.session.delete(itinerary)
        db.session.commit()
        return jsonify({"message": "Itinerary deleted successfully"})
    else:
        return jsonify({"message": "Itinerary not found"}), 404


# GET ALL DESTINATIONS PER ID
@app.route("/itinerary/<itinerary_id>/destinations", methods=["GET"])
def get_destinations_per_itinerary(itinerary_id):
    itinerary_destinations = ItineraryDestination.query.filter_by(
        itinerary_id=itinerary_id
    )
    output = []

    for id in itinerary_destinations:
        destination = Destination.query.filter_by(id=id.destination_id).first().json()
        output.append(destination)

    return output


if __name__ == "__main__":
    app.run(debug=True)
