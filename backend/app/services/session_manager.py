from flask import session
from app.extensions import db
from app.models.user import User
from datetime import datetime

def get_or_create_user():
    """Récupère l'utilisateur lié à la session ou en crée un nouveau."""
    session_id = session.sid  # identifiant unique de session Flask
    
    user = User.query.filter_by(session_id=session_id).first()
    
    if user is None:
        user = User(session_id=session_id)
        db.session.add(user)
        db.session.commit()
        session['is_new'] = True
    else:
        user.last_seen = datetime.utcnow()
        db.session.commit()
        session['is_new'] = False
    
    return user