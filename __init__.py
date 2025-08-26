from flask import Flask
from app.extensions import db
from app.routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/emotions.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Use your generated secret key
    app.config['SECRET_KEY'] = '16fbe0c6d0f359d342357340005b59a2'

    # Initialize the db instance
    db.init_app(app)

    with app.app_context():
        from app.models.models import EmotionEntry
        db.create_all()

    # Register routes
    register_routes(app)

    return app

