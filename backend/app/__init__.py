from flask import Flask
from .config import Config
from .extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Enregistrer les blueprints
    from .api.health import health_bp
    from .api.session import session_bp
    from .api.username import username_bp
    from .api.pipelines import pipelines_bp
    from .api.analysis import analysis_bp
    from .api.docs import docs_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(username_bp)
    app.register_blueprint(pipelines_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(docs_bp)
    
    return app