from flask import Blueprint, request, jsonify
from app.services.user_service import get_or_create_user
from app.services import pipeline_moma_service

pipelines_moma_bp = Blueprint('pipelines_moma', __name__)


@pipelines_moma_bp.route('/api/moma/pipelines', methods=['GET'])
def list_pipelines():
    user, _ = get_or_create_user()
    pipelines = pipeline_moma_service.get_pipelines(user.id)
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'graph_json': p.graph_json,
        'created_at': p.created_at.isoformat(),
        'updated_at': p.updated_at.isoformat(),
    } for p in pipelines])


@pipelines_moma_bp.route('/api/moma/pipelines', methods=['POST'])
def create_pipeline():
    user, _ = get_or_create_user()
    data = request.get_json()
    if not data or 'graph_json' not in data:
        return jsonify({'error': 'graph_json requis'}), 400

    pipeline = pipeline_moma_service.save_pipeline(
        user_id=user.id,
        name=data.get('name', 'Sans nom'),
        graph_json=data['graph_json'],
    )
    return jsonify({
        'id': pipeline.id,
        'name': pipeline.name,
        'graph_json': pipeline.graph_json,
        'created_at': pipeline.created_at.isoformat(),
    }), 201


@pipelines_moma_bp.route('/api/moma/pipelines/<int:pipeline_id>', methods=['GET'])
def get_pipeline(pipeline_id):
    user, _ = get_or_create_user()
    pipeline = pipeline_moma_service.get_pipeline(pipeline_id, user.id)
    if not pipeline:
        return jsonify({'error': 'Pipeline non trouvé'}), 404
    return jsonify({
        'id': pipeline.id,
        'name': pipeline.name,
        'graph_json': pipeline.graph_json,
        'created_at': pipeline.created_at.isoformat(),
        'updated_at': pipeline.updated_at.isoformat(),
    })


@pipelines_moma_bp.route('/api/moma/pipelines/<int:pipeline_id>', methods=['PUT'])
def update_pipeline(pipeline_id):
    user, _ = get_or_create_user()
    data = request.get_json()
    pipeline = pipeline_moma_service.update_pipeline(
        pipeline_id=pipeline_id,
        user_id=user.id,
        name=data.get('name'),
        graph_json=data.get('graph_json'),
    )
    if not pipeline:
        return jsonify({'error': 'Pipeline non trouvé'}), 404
    return jsonify({
        'id': pipeline.id,
        'name': pipeline.name,
        'graph_json': pipeline.graph_json,
        'updated_at': pipeline.updated_at.isoformat(),
    })


@pipelines_moma_bp.route('/api/moma/pipelines/<int:pipeline_id>', methods=['DELETE'])
def delete_pipeline(pipeline_id):
    user, _ = get_or_create_user()
    success = pipeline_moma_service.delete_pipeline(pipeline_id, user.id)
    if not success:
        return jsonify({'error': 'Pipeline non trouvé'}), 404
    return jsonify({'message': 'Pipeline supprimé'}), 200
