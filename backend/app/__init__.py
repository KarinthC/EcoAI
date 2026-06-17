from flask import Flask, session, jsonify
from .config import Config
from .extensions import db, migrate
from .models.user import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Les blueprints seront enregistrés plus tard, quand les modules existeront
    # from .api.auth import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.route('/api/health')
    def health():
        return {'status': 'ok'}


    @app.route('/api/session')
    def get_session():
        if 'user_id' not in session:
                import uuid
                session['user_id'] = str(uuid.uuid4())
                session['is_new'] = True
        else:
                session['is_new'] = False
                
        return {
                'user_id': session.get('user_id'),
                'is_new': session.get('is_new')
            }


    return app