from app.extensions import db
from datetime import datetime,timezone

class Pipeline(db.Model):
    __tablename__ = 'pipelines'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), default='Sans nom')
    graph_json = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relation bidirectionnelle (optionnelle mais pratique)
    user = db.relationship('User', backref=db.backref('pipelines', lazy=True))