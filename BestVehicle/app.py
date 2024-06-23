from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicles.db'

    db.init_app(app)

    from routes import routes
    routes(app, db)
    
    migrate = Migrate(app, db)

    return app