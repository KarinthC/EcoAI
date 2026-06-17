from flask import Flask, session, jsonify, request
from .config import Config
from .extensions import db, migrate
from .models.user import User
from datetime import datetime



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
            # Nouveau cookie : créer un User anonyme en base
            user = User()
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.public_id
            return jsonify({
                'user_id': user.public_id,
                'username': None,
                'is_new': True
            })
        
        # Cookie existant : retrouver l'utilisateur
        user = User.query.filter_by(public_id=session['user_id']).first()
        if not user:
            # Cas rare : user supprimé de la base ? On recrée.
            user = User(public_id=session['user_id'])
            db.session.add(user)
            db.session.commit()
        
        user.last_seen = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'user_id': user.public_id,
            'username': user.username,
            'is_new': False
        })


    @app.route('/api/username', methods=['POST'])
    def set_username():
        if 'user_id' not in session:
            return jsonify({'error': 'No session'}), 400
        
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username or len(username) < 2:
            return jsonify({'error': 'Nom trop court'}), 400
        
        user = User.query.filter_by(public_id=session['user_id']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Vérifier l'unicité du nom
        existing = User.query.filter_by(username=username).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'Ce nom est déjà pris'}), 409
        
        user.username = username
        db.session.commit()
        
        return jsonify({'username': user.username})


    return app