#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os
from datetime import datetime

def generate_excel_report(data, output_path):
    """İşlenmiş verilerden Excel raporu oluşturur"""
    
    # DataFrame oluştur
    df = pd.DataFrame(data)
    
    # Görsel URL'yi Excel'de sakla ama HTML'de görselleri kullan
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Büyük Beden Analizi', index=False)
    
    # Excel dosyasını güzelleştir
    workbook = writer.book
    worksheet = writer.sheets['Büyük Beden Analizi']
    
    # Format tanımlamaları
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    money_format = workbook.add_format({'num_format': '#,##0.00 ₺'})
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    
    # Sütun başlıklarını formatla
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    
    # Parasal değerleri formatla
    for col_num, col in enumerate(df.columns):
        if col in ['Ort. Alış', 'Ort. Satış']:
            worksheet.set_column(col_num, col_num, 12, money_format)
    
    # Sütun genişliklerini ayarla
    worksheet.set_column('A:A', 15)  # Model Kodu
    worksheet.set_column('B:B', 15)  # Barkod
    worksheet.set_column('C:C', 10)  # Beden
    worksheet.set_column('D:D', 12)  # Mevcut Stok
    worksheet.set_column('E:F', 12)  # Fiyatlar
    worksheet.set_column('G:J', 12)  # Satış değerleri
    worksheet.set_column('K:L', 18)  # Stok tahminleri
    worksheet.set_column('M:M', 50)  # Görsel URL
    
    # Kaydet
    writer.close()
    
    print(f"Excel raporu oluşturuldu: {output_path}")
    return output_path

def generate_html_report(data):
    """İşlenmiş verilerden HTML raporu oluşturur"""
    
    if not data or len(data) == 0:
        return "<div class='alert alert-warning'>Analiz edilecek veri bulunamadı!</div>"
    
    # Model kodlarına göre grupla
    grouped_data = {}
    for item in data:
        model_code = item.get('Model Kodu', '')
        if not model_code:  # Model kodu yoksa boş string olarak işaretlenir
            model_code = "Belirsiz Model"
            
        if model_code not in grouped_data:
            grouped_data[model_code] = []
        grouped_data[model_code].append(item)
    
    # HTML raporu oluştur
    html = """
    <style>
    .model-container {
        display: flex;
        margin-bottom: 40px;
        border-bottom: 1px solid #ccc;
        padding-bottom: 20px;
    }
    .model-image {
        width: 30%;
        min-width: 250px;
        padding-right: 20px;
    }
    .model-info {
        width: 70%;
        flex-grow: 1;
        overflow-x: auto;
    }
    .product-image {
        width: 100%;
        max-width: 300px;
        height: auto;
        object-fit: contain;
    }
    .model-code {
        font-weight: bold;
        font-size: 18px;
        background-color: #f2f2f2;
        padding: 10px;
        margin-bottom: 15px;
        border-radius: 4px;
    }
    .model-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
    }
    .model-table th {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        text-align: center;
        padding: 8px;
        position: sticky;
        top: 0;
        border: 1px solid #ddd;
    }
    .model-table td {
        padding: 8px;
        border: 1px solid #ddd;
        text-align: center;
    }
    .out-of-stock {
        background-color: #ffcccc;
    }
    .table-container {
        max-width: 100%;
        overflow-x: auto;
    }
    </style>
    """
    
    try:
        # Her model için bir tablo oluştur
        for model_code, items in grouped_data.items():
            # Görsel URL'yi bul
            image_url = None
            for item in items:
                if item.get('Görsel URL') and pd.notna(item.get('Görsel URL')):
                    image_url = item.get('Görsel URL')
                    break
            
            html += '<div class="model-container">'
            
            # Görsel solda
            html += '<div class="model-image">'
            if image_url:
                html += f'<img src="{image_url}" class="product-image" alt="Ürün görseli">'
            else:
                html += '<div class="no-image">Görsel Yok</div>'
            html += '</div>'
            
            # Tablo sağda
            html += '<div class="model-info">'
            html += f'<div class="model-code">Model: {model_code}</div>'
            
            # Bedenleri sırala
            sorted_items = sort_sizes(items)
            
            html += '<div class="table-container">'
            # Tablo oluştur
            html += '<table class="model-table">'
            html += '<tr><th>Beden</th><th>Mevcut Stok</th><th>Ort. Alış</th><th>Ort. Satış</th>'
            html += '<th>Top. Satış</th><th>90 Gün Satış</th><th>30 Gün Satış</th>'
            html += '<th>15 Gün Satış</th><th>Kaç Günlük Stok Var</th><th>Kaç Gündür Stok Yok</th>' # YENİ SÜTUN
            html += '<th>Stok Olsaydı Satış Tahmini</th></tr>'
            
            # Tablo satırlarını oluştur
            for item in sorted_items:
                # Stok durumuna göre CSS sınıfı belirle
                row_class = " class='out-of-stock'" if item.get('Mevcut Stok', 0) <= 0 else ""
                
                html += f"<tr{row_class}>"
                html += f"<td>{item.get('Beden', '-')}</td>"
                html += f"<td>{item.get('Mevcut Stok', 0)}</td>"
                
                # Ortalama fiyatlar
                ort_alis = item.get('Ort. Alış', 0)
                if pd.notna(ort_alis) and ort_alis > 0:
                    html += f"<td>{ort_alis:.2f} ₺</td>"
                else:
                    html += "<td>-</td>"
                
                ort_satis = item.get('Ort. Satış', 0)
                if pd.notna(ort_satis) and ort_satis > 0:
                    html += f"<td>{ort_satis:.2f} ₺</td>"
                else:
                    html += "<td>-</td>"
                
                # Satış adetleri
                html += f"<td>{item.get('Top. Satış', 0)}</td>"
                html += f"<td>{item.get('90 Gün Satış', 0)}</td>"
                html += f"<td>{item.get('30 Gün Satış', 0)}</td>"
                html += f"<td>{item.get('15 Gün Satış', 0)}</td>"
                
                # Stok yeterliliği
                html += f"<td>{item.get('Kaç Günlük Stok Var', '-')}</td>"
                
                # Kaç gündür stok yok (YENİ)
                html += f"<td>{item.get('Kaç Gündür Stok Yok', '-')}</td>"
                
                # Potansiyel kayıp
                html += f"<td>{item.get('Stok Olsaydı Satış Tahmini', '-')}</td>"
                
                html += "</tr>"
            
            html += '</table>'
            html += '</div>'  # table-container end
            html += '</div>'  # model-info end
            html += '</div>'  # model-container end
        
        return html
    except Exception as e:
        return f"<div class='alert alert-danger'>Rapor oluşturma hatası: {str(e)}</div>"

def sort_sizes(items):
    """Bedenleri doğru sıralama algoritması"""
    try:
        # Beden türlerini ayır
        numeric_sizes = []
        range_sizes = []
        letter_sizes = []
        other_sizes = []
        
        size_order = {
            's': 1, 'small': 1, 'sm': 1,
            'm': 2, 'medium': 2, 'md': 2,
            'l': 3, 'large': 3, 'lg': 3,
            'xl': 4, 'xlarge': 4, '1xl': 4,
            '2xl': 5, 'xxl': 5, '2x': 5,
            '3xl': 6, 'xxxl': 6, '3x': 6,
            '4xl': 7, 'xxxxl': 7, '4x': 7,
            '5xl': 8, 'xxxxxl': 8, '5x': 8,
        }
        
        for item in items:
            size = str(item.get('Beden', '')).lower().strip()
            
            # Sayısal beden (42, 44, 46, vs)
            if size.isdigit():
                numeric_sizes.append((int(size), item))
            # Aralık bedenleri (46-48, 50-52, vs)
            elif '-' in size and any(c.isdigit() for c in size):
                # İlk sayısal değere göre sırala
                try:
                    first_num = int(''.join([c for c in size.split('-')[0] if c.isdigit()]))
                    range_sizes.append((first_num, item))
                except:
                    other_sizes.append((size, item))
            # Harf bedenleri (S, M, L, XL, vs)
            elif size in size_order:
                letter_sizes.append((size_order[size], item))
            # Diğer (alfabetik sıralama)
            else:
                other_sizes.append((size, item))
        
        # Her grup kendi içinde sıralanır
        numeric_sizes.sort()
        range_sizes.sort()
        letter_sizes.sort()
        other_sizes.sort()
        
        # Tüm gruplar birleştirilir: Önce sayısal, sonra aralık, sonra harf, en son diğer bedenler
        sorted_items = []
        for _, item in numeric_sizes:
            sorted_items.append(item)
        for _, item in range_sizes:
            sorted_items.append(item)
        for _, item in letter_sizes:
            sorted_items.append(item)
        for _, item in other_sizes:
            sorted_items.append(item)
            
        return sorted_items
    except Exception as e:
        print(f"Beden sıralama hatası: {e}")
        return items  # Hata durumunda orijinal listeyi döndür