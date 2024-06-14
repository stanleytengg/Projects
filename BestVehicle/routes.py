from flask import render_template
from models import Vehicle

def routes(app, db):

    @app.route('/')
    def hello():
        return render_template('home.html')