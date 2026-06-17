from flask import Blueprint, session, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health')
def health():
    return {'status': 'ok'}