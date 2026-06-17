from flask import Blueprint, session, request, jsonify
from app.services.user_service import set_username_for_user

username_bp = Blueprint('username', __name__)

@username_bp.route('/api/username', methods=['POST'])
def set_username():
    if 'user_id' not in session:
        return jsonify({'error': 'No session'}), 400
    
    data = request.get_json()
    username = data.get('username', '').strip()
    
    success, message = set_username_for_user(session['user_id'], username)
    
    if not success:
        status = 400 if 'court' in message else 409 if 'pris' in message else 404
        return jsonify({'error': message}), status
    
    return jsonify({'username': message})