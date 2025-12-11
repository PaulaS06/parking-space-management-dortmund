from flask import Flask
# Import Flask, the web framework for building the API

from flask_sqlalchemy import SQLAlchemy
# Import SQLAlchemy to manage database models and interactions

from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
# Import Flask-RESTful classes:
# - Resource: base class for REST resources
# - Api: main REST API object
# - reqparse: argument parsing for POST/PUT requests
# - fields & marshal_with: define and serialize output fields
# - abort: return HTTP errors

app = Flask(__name__)
# Create a Flask application instance

api = Api(app)
# Create a Flask-RESTful API object associated with the app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# Configure SQLAlchemy to use an SQLite database file called "database.db"

db = SQLAlchemy(app)
# Initialize SQLAlchemy with the Flask app

class BasePriceModel(db.Model):
    # Define a database model (table) for storing base prices
    id = db.Column(db.Integer, primary_key=True)
    # 'id' is the primary key, auto-incrementing integer
    name = db.Column(db.String(120), unique=True, nullable=False)
    # 'name' is a string (max 120 chars), must be unique, cannot be null
    price = db.Column(db.Float)
    # 'price' is a floating point number

    def __repr__(self):
        return f"BasePrice(name = {self.name}, price = {self.price})"
    # Define a string representation for debugging/printing

baseprice_args = reqparse.RequestParser()
# Create a request parser for validating incoming POST data

baseprice_args.add_argument('name', type=str, required=True, help="Name not be blank")
# Add a required string argument 'name' with a custom help message

baseprice_args.add_argument('price', type=float, required=True, help="Base Price not be blank")
# Add a required float argument 'price' with a custom help message

baseprice_fields= {
    'id':fields.Integer,
    'name':fields.String,
    'price':fields.Float
}
# Define how to serialize the BasePriceModel fields when sending responses

class BasePrices(Resource):
    # Define a RESTful resource for handling /api/baseprices

    @marshal_with(baseprice_fields)
    def get(self):
        # GET request: return all base prices, serialized according to baseprice_fields
        prices = BasePriceModel.query.all()
        # Query all records from the BasePriceModel table
        return prices
        # Return the list of prices

    @marshal_with(baseprice_fields)
    def post(self):
        # POST request: add a new base price
        args = baseprice_args.parse_args()
        # Parse and validate incoming arguments
        new_price = BasePriceModel(name = args["name"], price=args["price"])
        # Create a new BasePriceModel instance with the submitted data
        db.session.add(new_price)
        # Add the new object to the database session
        db.session.commit()
        # Commit the transaction to save it permanently
        baseprices = BasePriceModel.query.all()
        # Query all records again to return the updated list
        return baseprices, 201 # HTTP 201: Created

api.add_resource(BasePrices, '/api/baseprices')
# Register the resource with the API at the endpoint /api/baseprices

if __name__ == "__main__":
    app.run(debug=True)
    # Run the Flask app in debug mode (auto-reload, detailed errors)

print("Rutas disponibles:")
for rule in app.url_map.iter_rules():
    print(rule, rule.methods)
# Print all routes and their allowed HTTP methods for debugging purposes
