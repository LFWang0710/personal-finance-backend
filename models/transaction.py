from db import db

class TransactionModel(db.Model):

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float(precision=3), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    card_info = db.Column(db.String(80), nullable=False)