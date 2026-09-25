from app.extensions import db
from datetime import datetime, timezone


class PipelineMoMa(db.Model):
    """Pipeline conforme au modèle de données MoMa.

    Table dédiée à la branche de démonstration MoMa : elle coexiste avec la
    table `pipelines` (branche principale) sans la modifier. Le graphe est
    stocké tel quel dans `graph_json` (nœuds typés MoMa + arêtes typées).
    """

    __tablename__ = 'pipelines_moma'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), default='Sans nom')
    graph_json = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    user = db.relationship('User', backref=db.backref('pipelines_moma', lazy=True))
