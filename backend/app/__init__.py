from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from .config import Config
from .extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Un seul proxy de confiance devant l'API (Nginx) : on lit X-Forwarded-*.
    # Sans cela, Flask se croit en HTTP et ne pose jamais le cookie Secure.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

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