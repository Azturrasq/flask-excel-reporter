#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_from_directory, flash
import os
from werkzeug.utils import secure_filename
from app.utils.data_loader import load_sales_data, load_stock_data, load_image_data
from app.utils.data_processor import process_data, filter_large_size_products
from app.utils.report_generator import generate_excel_report, generate_html_report
from datetime import datetime
import traceback

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Dosya yükleme işlemleri
        if 'sales_file' not in request.files or 'stock_file' not in request.files:
            flash('Satış veya stok dosyası seçilmedi', 'error')
            return redirect(request.url)
        
        sales_file = request.files['sales_file']
        stock_file = request.files['stock_file']
        image_file = request.files.get('image_file')  # İsteğe bağlı
        
        if sales_file.filename == '' or stock_file.filename == '':
            flash('Dosya seçilmedi', 'error')
            return redirect(request.url)
        
        if sales_file and allowed_file(sales_file.filename) and stock_file and allowed_file(stock_file.filename):
            # Klasörlerin varlığını kontrol et ve oluştur
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(os.path.join(upload_folder, 'sales'), exist_ok=True)
            os.makedirs(os.path.join(upload_folder, 'stock'), exist_ok=True)
            os.makedirs(os.path.join(upload_folder, 'images'), exist_ok=True)
            
            # Satış dosyasını kaydet
            sales_filename = secure_filename(sales_file.filename)
            sales_path = os.path.join(upload_folder, 'sales', sales_filename)
            sales_file.save(sales_path)
            
            # Stok dosyasını kaydet
            stock_filename = secure_filename(stock_file.filename)
            stock_path = os.path.join(upload_folder, 'stock', stock_filename)
            stock_file.save(stock_path)
            
            # Görsel dosyasını kaydet (eğer varsa)
            image_filename = None
            if image_file and image_file.filename != '' and allowed_file(image_file.filename):
                image_filename = secure_filename(image_file.filename)
                image_path = os.path.join(upload_folder, 'images', image_filename)
                image_file.save(image_path)
            
            # Session'a dosya yollarını kaydet
            return redirect(url_for('main.analyze', 
                                   sales=sales_filename, 
                                   stock=stock_filename, 
                                   images=image_filename,
                                   filter_large=request.form.get('filter_large', 'true')))
        else:
            flash('İzin verilen dosya formatları: xlsx, xls', 'error')
            
    return render_template('upload.html')

@main_bp.route('/analyze')
def analyze():
    sales_filename = request.args.get('sales')
    stock_filename = request.args.get('stock')
    image_filename = request.args.get('images')
    filter_large = request.args.get('filter_large', 'true').lower() == 'true'
    
    if not sales_filename or not stock_filename:
        flash("Dosya bilgileri eksik!", "error")
        return redirect(url_for('main.upload'))
    
    # Dosya yollarını oluştur
    sales_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'sales', sales_filename)
    stock_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'stock', stock_filename)
    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images', image_filename) if image_filename else None
    
    # Dosyaların varlığını kontrol et
    if not os.path.exists(sales_path):
        flash(f"Satış dosyası bulunamadı: {sales_filename}", "error")
        return redirect(url_for('main.upload'))
        
    if not os.path.exists(stock_path):
        flash(f"Stok dosyası bulunamadı: {stock_filename}", "error")
        return redirect(url_for('main.upload'))
    
    # Verileri yükle
    try:
        print("Satış verisi yükleniyor...")
        sales_df = load_sales_data(sales_path)
        print("Stok verisi yükleniyor...")
        stock_df = load_stock_data(stock_path)
        print("Görsel verisi yükleniyor...")
        image_df = load_image_data(image_path) if image_path and os.path.exists(image_path) else None
        
        # Büyük beden ürünlerini filtrele (eğer seçildiyse)
        if filter_large:
            print("Büyük beden ürünleri filtreleniyor...")
            filtered_sales = filter_large_size_products(sales_df)
        else:
            filtered_sales = sales_df
        
        print("Veri işleniyor...")
        # Verileri işle
        processed_data = process_data(filtered_sales, stock_df, image_df)
        
        # Veri kontrolü
        if not processed_data or len(processed_data) == 0:
            flash("İşlenecek veri bulunamadı. Veri dosyalarınızı kontrol edin.", "warning")
            return redirect(url_for('main.upload'))
        
        print("Excel raporu oluşturuluyor...")
        # Rapor klasörünü kontrol et ve oluştur
        os.makedirs(current_app.config['RESULTS_FOLDER'], exist_ok=True)
        
        # Rapor dosyasını oluştur
        today = datetime.now().strftime("%Y-%m-%d")
        report_filename = f"buyuk_beden_raporu_{today}.xlsx"
        report_path = os.path.join(current_app.config['RESULTS_FOLDER'], report_filename)
        
        generate_excel_report(processed_data, report_path)
        
        print("HTML rapor oluşturuluyor...")
        # HTML raporu oluştur
        html_report = generate_html_report(processed_data)
        
        return render_template(
            'report.html',
            report_data=processed_data,
            html_report=html_report,
            download_url=url_for('main.download_report', filename=report_filename)
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"HATA: {str(e)}")
        print(error_details)
        flash(f'Veri analizi sırasında hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.upload'))

@main_bp.route('/download/<path:filename>')
def download_report(filename):
    return send_from_directory(
        directory=current_app.config['RESULTS_FOLDER'], 
        path=filename, 
        as_attachment=True
    )