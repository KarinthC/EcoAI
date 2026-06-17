from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instances non initialisées
db = SQLAlchemy()
migrate = Migrate()
