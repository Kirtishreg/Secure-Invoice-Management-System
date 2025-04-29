from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from routes import app as main_app
from models import *

# Initialize the database and login manager
migrate = Migrate()
login_manager = LoginManager()  # Moved here

def create_app():
    app = Flask(__name__)

    # Configure database
    app.config['SECRET_KEY'] = 'your_unique_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database and migration
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize LoginManager with the app
    login_manager.init_app(app)  # Initialize the login manager with the app
    login_manager.login_view = 'main.login'  # Set the login view to the blueprint's login

    # Register the routes blueprint
    app.register_blueprint(main_app)

    return app

# Create the app instance
app = create_app()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(ssl_context='adhoc', debug=True)  # Run with SSL for HTTPS and enable debug mode
