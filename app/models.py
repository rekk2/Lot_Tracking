# app/models.py

from . import db

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String(50), nullable=False)
    lot_number = db.Column(db.String(50), nullable=False)
    receipt_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(50), nullable=False)
    inspection_status = db.Column(db.String(20), default='RECEIVED')
    qr_code_id = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)  # Add this line
