from app.extensions import db
from datetime import datetime,timezone
import uuid

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50),  nullable=True)  # NULL tant que non choisi
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_seen = db.Column(db.DateTime, default=datetime.now(timezone.utc))
