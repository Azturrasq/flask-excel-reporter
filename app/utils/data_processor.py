#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def filter_non_return_sales(sales_df):
    if 'Status' in sales_df.columns:
        return sales_df[~sales_df['Status'].str.contains('Return', case=False, na=False)]
    return sales_df

def extract_size_info(option):
    if isinstance(option, str):
        if " - " in option:
            return option.split(" - ")[0].strip()
    return option

def calculate_average_prices(df, barcode):
    product_df = df[df['Barcode'] == barcode]
    purchase_col = next((col for col in product_df.columns if 'purchase' in col.lower()), None)
    sale_col = next((col for col in product_df.columns if 'sale' in col.lower()), None)
    
    if purchase_col and sale_col:
        quantity_col = next((col for col in product_df.columns if 'quantity' in col.lower()), None)
        
        if quantity_col:
            total_purchase = (product_df[purchase_col] * product_df[quantity_col]).sum()
            total_sale = (product_df[sale_col] * product_df[quantity_col]).sum()
            total_quantity = product_df[quantity_col].sum()
            
            if total_quantity > 0:
                avg_purchase = total_purchase / total_quantity
                avg_sale = total_sale / total_quantity
                return avg_purchase, avg_sale
            
        return product_df[purchase_col].mean(), product_df[sale_col].mean()
    
    return None, None

def calculate_sales_for_period(df, barcode, date_col, days):
    if not date_col or days <= 0:
        return 0
    
    start_date = datetime.now() - pd.Timedelta(days=days)
    recent_sales = df[(df['Barcode'] == barcode) & (df[date_col] >= start_date)]
    
    if len(recent_sales) == 0:
        return 0
    
    quantity_col = next((col for col in recent_sales.columns if 'quantity' in col.lower()), None)
    
    if not quantity_col:
        return 0
    
    return recent_sales[quantity_col].sum()

def stock_sufficiency_days(barcode, stock_quantity, sales_df, date_col):
    if not date_col or stock_quantity <= 0:
        return "-"
    
    last_30_days = datetime.now() - pd.Timedelta(days=30)
    recent_sales = sales_df[(sales_df['Barcode'] == barcode) & (sales_df[date_col] >= last_30_days)]
    
    if len(recent_sales) == 0:
        return "-"
    
    quantity_col = next((col for col in recent_sales.columns if 'quantity' in col.lower()), None)
    
    if not quantity_col:
        return "-"
    
    daily_average = recent_sales[quantity_col].sum() / 30
    
    if daily_average > 0:
        sufficient_days = stock_quantity / daily_average
        return round(sufficient_days)
    else:
        return "-"

def potential_sales_loss(barcode, size, sales_df):
    product_sales = sales_df[sales_df['Barcode'] == barcode]
    
    date_col = next((col for col in product_sales.columns if 'date' in col.lower()), None)
    if not date_col:
        return "-"
    
    if 'Size' not in product_sales.columns:
        return "-"
    
    size_sales = product_sales[product_sales['Size'] == size]
    size_days = set(size_sales[date_col].dt.date) if len(size_sales) > 0 else set()
    
    all_days = set(product_sales[date_col].dt.date) if len(product_sales) > 0 else set()
    
    missing_days = all_days - size_days
    
    if not missing_days:
        return 0
    
    quantity_col = next((col for col in size_sales.columns if 'quantity' in col.lower()), None)
    if not quantity_col:
        return "-"
    
    if len(size_sales) > 0:
        daily_average = size_sales[quantity_col].sum() / len(size_days) if len(size_days) > 0 else 0
        lost_sales = daily_average * len(missing_days)
        return round(lost_sales)
    
    return "-"

def filter_large_size_products(sales_df):
    """Sadece 'büyük beden' içeren ürünleri filtreler"""
    if 'Ürün' in sales_df.columns:
        large_size_df = sales_df[sales_df['Ürün'].str.contains('büyük beden', case=False, na=False)]
        
        if len(large_size_df) > 0:
            print(f"Büyük beden ürünleri filtrelendi: {len(large_size_df)} satır.")
            return large_size_df
        else:
            print("Büyük beden içeren ürün bulunamadı! Tüm verilerle devam ediliyor.")
            
    return sales_df

def process_data(sales_df, stock_df, image_df=None):
    """Satış ve stok verilerini işleyerek model-beden bazlı analiz sonuçları üretir"""
    
    # Veri kontrolü
    if sales_df is None or stock_df is None:
        print("Satış veya stok verisi eksik!")
        return []
    
    if len(sales_df) == 0 or len(stock_df) == 0:
        print("Satış veya stok verisi boş!")
        return []
    
    # Sütunların varlığını kontrol et
    required_sales_columns = ['Barkod']
    required_stock_columns = ['Barkod', 'Stok']
    
    missing_sales_cols = [col for col in required_sales_columns if col not in sales_df.columns]
    missing_stock_cols = [col for col in required_stock_columns if col not in stock_df.columns]
    
    if missing_sales_cols:
        print(f"Satış verisinde gerekli sütunlar eksik: {missing_sales_cols}")
        print(f"Mevcut sütunlar: {sales_df.columns.tolist()}")
        raise ValueError(f"Satış verisi eksik sütunlar içeriyor: {missing_sales_cols}")
        
    if missing_stock_cols:
        print(f"Stok verisinde gerekli sütunlar eksik: {missing_stock_cols}")
        print(f"Mevcut sütunlar: {stock_df.columns.tolist()}")
        raise ValueError(f"Stok verisi eksik sütunlar içeriyor: {missing_stock_cols}")
        
    # Model kodu sütununu bul
    model_column = None
    possible_model_columns = ['Grup MPN', 'grup mpn', 'Grup_MPN', 'Model Kodu', 'model kodu', 'Model', 'model', 'Ürün Kodu', 'ürün kodu']
    
    for col in possible_model_columns:
        if col in stock_df.columns:
            model_column = col
            print(f"Model kodu sütunu bulundu: {model_column}")
            break
    
    if not model_column:
        print("Model kodu sütunu bulunamadı. Barkod'lar model olarak kullanılacak.")
    
    # Veri tiplerini sağlamlaştır
    sales_df['Barkod'] = sales_df['Barkod'].astype(str)
    stock_df['Barkod'] = stock_df['Barkod'].astype(str)
    
    # Ortak barkodları bul
    sales_barcodes = set(sales_df['Barkod'].unique())
    stock_barcodes = set(stock_df['Barkod'].unique())
    common_barcodes = sales_barcodes.intersection(stock_barcodes)
    
    print(f"Satış verisinde {len(sales_barcodes)} farklı barkod var.")
    print(f"Stok verisinde {len(stock_barcodes)} farklı barkod var.")
    print(f"Her iki veride ortak {len(common_barcodes)} barkod var.")
    
    if len(common_barcodes) == 0:
        print("Ortak barkod bulunamadı! Satış ve stok verilerini kontrol edin.")
        return []
    
    # Barkod ve model kodu eşleştirmesi
    barkod_model_dict = {}
    
    if model_column:
        for _, row in stock_df.iterrows():
            if pd.notna(row['Barkod']) and pd.notna(row[model_column]):
                barkod_model_dict[str(row['Barkod'])] = str(row[model_column])
                
    # Model gruplarını oluştur
    model_groups = {}
    
    # Her barkodu işle
    for barkod in common_barcodes:
        # Model kodunu bul
        model_code = barkod_model_dict.get(barkod, barkod)
        
        if model_code not in model_groups:
            model_groups[model_code] = []
            
        model_groups[model_code].append(barkod)
    
    # Sonuç veri yapısını oluştur
    result_data = []
    
    # İşlenen barkodları takip et
    processed_count = 0
    
    for model_code, barcodes in model_groups.items():
        # Model için görsel URL'sini bul
        image_url = None
        if image_df is not None:
            for barcode in barcodes:
                if 'Barkod' in image_df.columns:
                    image_cols = [col for col in image_df.columns if 'resim' in col.lower() or 'görsel' in col.lower() or 'url' in col.lower()]
                    if image_cols:
                        image_col = image_cols[0]
                        image_df['Barkod'] = image_df['Barkod'].astype(str)
                        image_row = image_df[image_df['Barkod'] == barcode]
                        if len(image_row) > 0 and pd.notna(image_row[image_col].iloc[0]):
                            image_url = image_row[image_col].iloc[0]
                            break
        
        # Her barkod için detay bilgileri hesapla
        for barcode in barcodes:
            try:
                processed_count += 1
                print(f"İşlenen: {processed_count}/{len(common_barcodes)} - Barkod: {barcode}")
                
                # Satış verileri
                sales_rows = sales_df[sales_df['Barkod'] == barcode]
                
                # Stok verisi
                stock_row = stock_df[stock_df['Barkod'] == barcode]
                if len(stock_row) == 0:
                    print(f"UYARI: {barcode} barkodu için stok verisi bulunamadı")
                    continue
                    
                stock_amount = stock_row['Stok'].iloc[0] if len(stock_row) > 0 and 'Stok' in stock_row.columns else 0
                
                # Beden bilgisi
                size = "-"
                if 'Beden' in sales_rows.columns and len(sales_rows) > 0:
                    size_values = sales_rows['Beden'].dropna().unique()
                    if len(size_values) > 0:
                        size = size_values[0]
                elif 'Beden' in stock_row.columns and len(stock_row) > 0:
                    size = stock_row['Beden'].iloc[0]
                elif 'Seçenek' in sales_rows.columns and len(sales_rows) > 0:
                    size_values = sales_rows['Seçenek'].dropna().unique()
                    if len(size_values) > 0:
                        size = str(size_values[0]).split(' - ')[0] if ' - ' in str(size_values[0]) else size_values[0]
                
                # Burada veri işleme kodları devam eder
                # ... mevcut kodlar ...
                
                # Sonuç veri yapısına ekle
                result_data.append({
                    "Model Kodu": model_code,
                    "Barkod": barcode,
                    "Beden": size,
                    "Mevcut Stok": stock_amount,
                    # ... diğer alanlar ...
                })
            except Exception as e:
                print(f"Barkod {barcode} işlenirken hata: {str(e)}")
    
    print(f"Toplam {len(result_data)} veri satırı oluşturuldu")
    return result_data