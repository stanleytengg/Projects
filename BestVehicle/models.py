from app import db

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(20), nullable=False)
    model = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    miles = db.Column(db.String(20), nullable=False)

    def get_id(self):
        return self.id