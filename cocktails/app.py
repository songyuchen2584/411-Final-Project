from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from werkzeug.exceptions import BadRequest, Unauthorized
# from flask_cors import CORS

from config import ProductionConfig
from cocktail_maker.models.user_model import Users
from cocktail_maker.db import db
from cocktail_maker.models.drink_model import Drink
from cocktail_maker.models.drink_list_model import DrinkListModel

# Load environment variables from .env file
load_dotenv()

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    with app.app_context():
        db.create_all()  # Recreate all tables

    ####################################################
    #
    # Healthchecks
    #
    ####################################################


    @app.route('/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.
        """
        app.logger.info('Health check')
        return make_response(jsonify({'status': 'healthy'}), 200)

    ####################################################
    #
    # UserManagement
    #
    ####################################################

    # Define routes
    @app.route("/create-account", methods=["POST"])
    def create_account():
        """
        Creates a new user account.
    
        Request Format:
            JSON:
            {
                "username": "string",
                "password": "string"
            }
    
        Response Format:
            201 success if account created successfully.
            400 error if username and password not entered or if username already exists. 
    
        Returns:
            A JSON response indicating success or failure of the account creation process.
        """
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        try:
            Users.create_user(username, password)
            return jsonify({"message": "Account created successfully"}), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/login", methods=["POST"])
    def login():
        """
        Log in a user by verifying their password.
    
        Request Format:
            JSON:
            {
                "username": "string",
                "password": "string"
            }
    
        Response Format:
            200 success message if login is successful.
            400 error if username and password aren't entered.
            401 error for invalid credentials.
            404 error if username not found.
    
        Returns:
            A JSON response indicating whether the login was successful or why it failed.
        """
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        try:
            if Users.check_password(username, password):
                return jsonify({"message": "Login successful"}), 200
            else:
                return jsonify({"error": "Invalid credentials"}), 401
        except ValueError as e:
            return jsonify({"error": str(e)}), 404

    @app.route("/update-password", methods=["POST"])
    def update_password():
        """
        Update the password for an existing user.
    
        Request Format:
            JSON:
            {
                "username": "string",
                "new_password": "string"
            }
    
        Response Format:
            200 success message if password updated successfully.
            400 error if username and/or new password not entered.
            404 error if username not found.
    
        Returns:
            A JSON response indicating success or failure of the password update process.
        """
        data = request.get_json()
        username = data.get("username")
        new_password = data.get("new_password")

        if not username or not new_password:
            return jsonify({"error": "Username and new password are required"}), 400

        try:
            Users.update_password(username, new_password)
            return jsonify({"message": "Password updated successfully"}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404


    ####################################################
    #
    # Drinks
    #
    ####################################################

    @app.route('/random-drink', methods=['GET'])
    def fetch_random_drink():
        """
        Fetch a random drink from the CocktailDB API.
        """
        try:
            random_drink = Drink.get_random_drink()
            return jsonify({'status': 'success', 'drink': random_drink}), 200
        except RuntimeError as e:
            app.logger.error("Failed to fetch random drink: %s", e)
            return jsonify({'error': str(e)}), 500

    @app.route('/drink/<string:drink_name>', methods=['GET'])
    def fetch_drink_by_name(drink_name: str):
        """
        Fetch a drink by name from the CocktailDB API.
        """
        try:
            drink = Drink.get_drink_by_name(drink_name)
            return jsonify({'status': 'success', 'drink': drink}), 200
        except ValueError as e:
            app.logger.warning("Drink not found: %s", e)
            return jsonify({'error': str(e)}), 404
        except RuntimeError as e:
            app.logger.error("Failed to fetch drink by name: %s", e)
            return jsonify({'error': str(e)}), 500

    @app.route('/drink/<string:drink_name>/alcoholic', methods=['GET'])
    def check_drink_alcoholic(drink_name: str):
        """
        Check if a drink is alcoholic based on its name.
        """
        try:
            app.logger.info(f"Checking if drink '{drink_name}' is alcoholic.")
            is_alcoholic = Drink.is_drink_alcoholic(drink_name)
            app.logger.info(f"Alcoholic status for '{drink_name}': {is_alcoholic}")
            return jsonify({'status': 'success', 'is_alcoholic': is_alcoholic}), 200
        except ValueError as e:
            app.logger.warning(f"Drink not found or invalid data: {e}")
            return jsonify({'error': str(e)}), 404
        except RuntimeError as e:
            app.logger.error(f"Failed to determine if drink is alcoholic: {e}")
            return jsonify({'error': str(e)}), 500
            
    drink_list = DrinkListModel()

    @app.route('/create-drink', methods=['POST'])
    def add_drink() -> Response:
        app.logger.info('Creating new drink')
        try:
            data = request.get_json()
            drink_name = data.get('name')

            if not drink_name:
                raise BadRequest("Drink name is required.")
            
            add_response = drink_list.add_drink(drink_name)

            if "not found" in add_response:
                raise BadRequest("Drink not found in the external API.") 
            
            drink = next((d for d in drink_list.drinks if d.name.lower() == drink_name.lower()), None)

            app.logger.info(f"Drink added: {drink.name}")
            return make_response(jsonify({'status': 'Drink added', 'drink': drink.to_dict()}), 201)

        except Exception as e:
            app.logger.error(f"Failed to add drink: {str(e)}")
            return make_response(jsonify({'error': str(e)}), 500)
        
    @app.route('/remove-drink', methods=['POST'])
    def remove_drink() -> Response:
        app.logger.info('Removing drink')

        try:
            data = request.get_json()
            name = data.get('name')

            if not name:
                raise BadRequest("Drink name is required.")
            
            drink_list.remove_drink(name)
            app.logger.info(f"Drink removed: {name}")
            return make_response(jsonify({'status': 'Drink removed', 'id': name}), 200)
        
        except ValueError as e:
            return make_response(jsonify({'error': str(e)}), 400)

        
    @app.route('/list-drinks', methods=['GET'])
    def list_drinks() -> Response:
        app.logger.info('Listing all drinks in alphabetical order')
        try:
            drinks_json = drink_list.list_drinks_in_alphabetical_order()
            return jsonify(drinks_json)
        
        except Exception as e:
            app.logger.error(f"Failed to list drinks: {str(e)}")
            return make_response(jsonify({'error': 'Failed to retrieve drinks'}), 500)

    @app.route('/init-db', methods=['POST'])
    def init_db():
        """
        Initialize or recreate database tables.

        This route initializes the database tables defined in the SQLAlchemy models.
        If the tables already exist, they are dropped and recreated to ensure a clean
        slate. Use this with caution as all existing data will be deleted.

        Returns:
            Response: A JSON response indicating the success or failure of the operation.

        Logs:
            Logs the status of the database initialization process.
        """
        try:
            with app.app_context():
                app.logger.info("Dropping all existing tables.")
                db.drop_all()  # Drop all existing tables
                app.logger.info("Creating all tables from models.")
                db.create_all()  # Recreate all tables
            app.logger.info("Database initialized successfully.")
            return jsonify({"status": "success", "message": "Database initialized successfully."}), 200
        except Exception as e:
            app.logger.error("Failed to initialize database: %s", str(e))
            return jsonify({"status": "error", "message": "Failed to initialize database."}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
