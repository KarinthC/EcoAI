import uuid
from datetime import datetime
from flask import session
from app.extensions import db
from app.models.user import User

def get_or_create_user():
    if 'user_id' not in session:
        user = User()
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.public_id
        return user, True
    
    user = User.query.filter_by(public_id=session['user_id']).first()
    if not user:
        user = User(public_id=session['user_id'])
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.public_id
        return user, True
    
    user.last_seen = datetime.utcnow()
    db.session.commit()
    return user, False

def set_username_for_user(public_id, username):
    if not username or len(username) < 2:
        return False, "Nom trop court (min. 2 caractères)"
    
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return False, "Utilisateur introuvable"
    
    user.username = username
    db.session.commit()
    return True, username