#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    
    # Uygulama yapılandırması
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
    app.config['DEBUG'] = os.environ.get('FLASK_ENV', 'development') != 'production'
    
    # Uygulama klasörleri
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', os.path.join(base_dir, 'data'))
    app.config['RESULTS_FOLDER'] = os.environ.get('RESULTS_FOLDER', os.path.join(base_dir, 'results'))
    
    # Klasörlerin varlığını kontrol et ve oluştur
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'sales'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'stock'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'), exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    
    # Blueprint'leri kaydet
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

# Render için uyumlu app örneği oluştur
app = create_app()