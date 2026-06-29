from flask import Blueprint, request, jsonify, session
from app.services.user_service import get_or_create_user
from app.services.carbon.orchestrator import compute_impact

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/api/analyze', methods=['POST'])
def analyze_pipeline():
    # Vérification de la session (l'utilisateur doit être connecté)
    user, _ = get_or_create_user()
    data = request.get_json()
    if not data or 'nodes' not in data:
        return jsonify({'error': 'Format invalide'}), 400
    
    result = compute_impact(data)
    return jsonify(result), 200