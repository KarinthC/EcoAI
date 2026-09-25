from app.extensions import db
from app.models.pipeline_moma import PipelineMoMa


def save_pipeline(user_id, name, graph_json):
    """Crée un nouveau pipeline MoMa pour l'utilisateur."""
    pipeline = PipelineMoMa(
        user_id=user_id,
        name=name or 'Sans nom',
        graph_json=graph_json,
    )
    db.session.add(pipeline)
    db.session.commit()
    return pipeline


def update_pipeline(pipeline_id, user_id, name=None, graph_json=None):
    """Met à jour un pipeline MoMa existant (vérifie qu'il appartient à l'utilisateur)."""
    pipeline = PipelineMoMa.query.filter_by(id=pipeline_id, user_id=user_id).first()
    if not pipeline:
        return None
    if name is not None:
        pipeline.name = name
    if graph_json is not None:
        pipeline.graph_json = graph_json
    db.session.commit()
    return pipeline


def delete_pipeline(pipeline_id, user_id):
    """Supprime un pipeline MoMa."""
    pipeline = PipelineMoMa.query.filter_by(id=pipeline_id, user_id=user_id).first()
    if not pipeline:
        return False
    db.session.delete(pipeline)
    db.session.commit()
    return True


def get_pipelines(user_id):
    """Liste tous les pipelines MoMa d'un utilisateur."""
    return (
        PipelineMoMa.query
        .filter_by(user_id=user_id)
        .order_by(PipelineMoMa.updated_at.desc())
        .all()
    )


def get_pipeline(pipeline_id, user_id):
    """Récupère un pipeline MoMa spécifique."""
    return PipelineMoMa.query.filter_by(id=pipeline_id, user_id=user_id).first()
