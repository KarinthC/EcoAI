from flask import Blueprint, session, jsonify
from app.services.user_service import get_or_create_user

session_bp = Blueprint('session', __name__)

@session_bp.route('/api/session')
def get_session():
    user, is_new = get_or_create_user()
    return jsonify({
        'user_id': user.public_id,
        'username': user.username,
        'is_new': is_new
    })