from app import create_app

app = create_app()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Büyük Beden Rapor Uygulaması')
    parser.add_argument('--network', action='store_true', help='Ağ üzerinden erişim için')
    parser.add_argument('--port', type=int, default=5000, help='Bağlantı noktası (varsayılan: 5000)')
    parser.add_argument('--debug-data', action='store_true', help='Veri dosyalarını inceleme modunda başlat')
    
    args = parser.parse_args()
    
    if args.debug_data:
        # Veri dosyalarını inceleme modu
        print("Veri inceleme modu başlatılıyor...")
        import pandas as pd
        import os
        from app.utils.data_loader import load_sales_data, load_stock_data
        
        data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        sales_folder = os.path.join(data_folder, 'sales')
        stock_folder = os.path.join(data_folder, 'stock')
        
        # Klasörleri oluştur
        os.makedirs(sales_folder, exist_ok=True)
        os.makedirs(stock_folder, exist_ok=True)
        
        # En son yüklenen dosyaları bul
        try:
            sales_files = [f for f in os.listdir(sales_folder) if f.endswith('.xlsx') or f.endswith('.xls')]
            stock_files = [f for f in os.listdir(stock_folder) if f.endswith('.xlsx') or f.endswith('.xls')]
            
            if sales_files:
                latest_sales = os.path.join(sales_folder, sales_files[-1])
                print(f"En son yüklenen satış dosyası: {sales_files[-1]}")
                try:
                    df = pd.read_excel(latest_sales)
                    print(f"Satış dosyası sütunları: {df.columns.tolist()}")
                    print(f"Örnek veri (ilk 5 satır):")
                    print(df.head())
                except Exception as e:
                    print(f"Dosya okuma hatası: {e}")
                    
            if stock_files:
                latest_stock = os.path.join(stock_folder, stock_files[-1])
                print(f"\nEn son yüklenen stok dosyası: {stock_files[-1]}")
                try:
                    df = pd.read_excel(latest_stock)
                    print(f"Stok dosyası sütunları: {df.columns.tolist()}")
                    print(f"Örnek veri (ilk 5 satır):")
                    print(df.head())
                except Exception as e:
                    print(f"Dosya okuma hatası: {e}")
        except Exception as e:
            print(f"Veri inceleme hatası: {e}")
            
    elif args.network:
        # Ağ üzerinden erişim için
        app.run(debug=True, host='0.0.0.0', port=args.port)
    else:
        # Sadece yerel erişim
        app.run(debug=True, port=args.port)