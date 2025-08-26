from app import create_app
from app.extensions import db
from app.models.models import User, EmotionEntry

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created.")
