#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os

def load_sales_data(sales_path):
    """Satış verilerini yükleyen fonksiyon"""
    try:
        print(f"Satış verisi okunuyor: {sales_path}")
        sales_df = pd.read_excel(sales_path)
        print(f"Satış verileri yüklendi: {len(sales_df)} satır.")
        
        # Sütun isimlerini standartlaştır
        sales_df.columns = [col.strip() for col in sales_df.columns]
        
        # Barkod sütununu bul ve standartlaştır
        barkod_col = None
        for col in sales_df.columns:
            if col.lower() == 'barkod':
                barkod_col = col
                break
        
        if barkod_col is None:
            raise ValueError("Satış dosyasında Barkod sütunu bulunamadı!")
        
        # Barkod sütununu yeniden adlandır (standartlaştır)
        sales_df.rename(columns={barkod_col: 'Barkod'}, inplace=True)
        
        # Barkod sütununu string'e çevir
        sales_df['Barkod'] = sales_df['Barkod'].astype(str)
        
        # İadeleri filtrele
        if 'Durum' in sales_df.columns:
            filtered_df = sales_df[~sales_df['Durum'].str.contains('İade', case=False, na=False)]
            print(f"İadeler hariç satış kayıtları: {len(filtered_df)} satır.")
            sales_df = filtered_df
        
        # Tarih sütununu düzenle
        date_col = None
        for col in sales_df.columns:
            if 'tarih' in col.lower():
                date_col = col
                break
        
        if date_col:
            try:
                sales_df[date_col] = pd.to_datetime(sales_df[date_col], errors='coerce')
                print(f"Tarih sütunu dönüştürüldü: {date_col}")
            except Exception as e:
                print(f"Tarih sütunu dönüştürülemedi: {date_col}, hata: {str(e)}")
        
        # Seçenek sütunundan beden bilgisi ayıkla
        if 'Seçenek' in sales_df.columns:
            sales_df['Beden'] = sales_df['Seçenek'].apply(extract_size_info)
            print("Beden bilgileri çıkarıldı.")
        
        return sales_df
        
    except Exception as e:
        print(f"Satış verileri yüklenirken hata: {str(e)}")
        raise e

def load_stock_data(stock_path):
    """Stok verilerini yükleyen fonksiyon"""
    try:
        print(f"Stok verisi okunuyor: {stock_path}")
        stock_df = pd.read_excel(stock_path)
        print(f"Stok verileri yüklendi: {len(stock_df)} satır.")
        
        # Sütun isimlerini standartlaştır
        stock_df.columns = [col.strip() for col in stock_df.columns]
        
        # Barkod sütununu bul ve standartlaştır
        barkod_col = None
        for col in stock_df.columns:
            if col.lower() == 'barkod':
                barkod_col = col
                break
        
        if barkod_col is None:
            raise ValueError("Stok dosyasında Barkod sütunu bulunamadı!")
        
        # Barkod sütununu yeniden adlandır (standartlaştır)
        stock_df.rename(columns={barkod_col: 'Barkod'}, inplace=True)
        
        # Stok sütununu bul ve standartlaştır
        stok_col = None
        for col in stock_df.columns:
            if col.lower() == 'stok' or 'miktar' in col.lower():
                stok_col = col
                break
        
        if stok_col is None:
            raise ValueError("Stok dosyasında Stok/Miktar sütunu bulunamadı!")
        
        # Stok sütununu yeniden adlandır (standartlaştır)
        stock_df.rename(columns={stok_col: 'Stok'}, inplace=True)
        
        # Barkod sütununu string'e çevir
        stock_df['Barkod'] = stock_df['Barkod'].astype(str)
        
        print(f"Stok verileri hazır. Sütunlar: {stock_df.columns.tolist()}")
        return stock_df
    except Exception as e:
        print(f"Stok verileri yüklenirken hata: {str(e)}")
        raise e

def load_image_data(image_path):
    """Ürün görselleri verilerini yükleyen fonksiyon"""
    if not image_path:
        return None
        
    try:
        print(f"Görsel verisi okunuyor: {image_path}")
        image_df = pd.read_excel(image_path)
        print(f"Görsel verileri yüklendi: {len(image_df)} satır.")
        
        # Sütun isimlerini standartlaştır
        image_df.columns = [col.strip() for col in image_df.columns]
        
        # Barkod sütununu bul ve standartlaştır
        barkod_col = None
        for col in image_df.columns:
            if col.lower() == 'barkod':
                barkod_col = col
                break
        
        if barkod_col is None:
            print("UYARI: Görsel dosyasında Barkod sütunu bulunamadı!")
            return None
        
        # Barkod sütununu yeniden adlandır (standartlaştır)
        image_df.rename(columns={barkod_col: 'Barkod'}, inplace=True)
        
        # Görsel URL sütununu bul
        image_col = None
        for col in image_df.columns:
            if 'resim' in col.lower() or 'görsel' in col.lower() or 'url' in col.lower() or 'image' in col.lower():
                image_col = col
                break
        
        if image_col is None:
            print("UYARI: Görsel dosyasında görsel/resim/URL sütunu bulunamadı!")
            return None
        
        # Görsel URL sütununu yeniden adlandır (standartlaştır)
        image_df.rename(columns={image_col: 'Görsel URL'}, inplace=True)
        
        # Barkod sütununu string'e çevir
        image_df['Barkod'] = image_df['Barkod'].astype(str)
        
        return image_df
    except Exception as e:
        print(f"Görsel verileri yüklenirken hata: {str(e)}")
        return None

def extract_size_info(option):
    """Seçenek sütunundan beden bilgisini ayıklayan yardımcı fonksiyon"""
    try:
        if pd.isna(option):
            return None
            
        if isinstance(option, str):
            # Örnek: "48 - Siyah Gri" -> "48" veya "XL - Lacivert" -> "XL"
            if " - " in option:
                size = option.split(" - ")[0].strip()
                return size
            # Başka formatlar için kontrol
            elif "Beden:" in option:
                parts = option.split("Beden:")
                if len(parts) > 1:
                    size = parts[1].strip()
                    # Eğer birden fazla bilgi varsa ilk boşluğa kadar al
                    if " " in size:
                        size = size.split(" ")[0].strip()
                    return size
    except Exception as e:
        print(f"Beden ayıklama hatası: {str(e)}")
    return option