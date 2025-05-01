from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SalesData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), nullable=False)
    model_code = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(10), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    average_purchase_price = db.Column(db.Float, nullable=False)
    average_sale_price = db.Column(db.Float, nullable=False)
    total_sales = db.Column(db.Integer, nullable=False)
    sales_date = db.Column(db.DateTime, nullable=False)

class StockData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), nullable=False)
    model_code = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class VisualData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)