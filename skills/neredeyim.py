def neredeyim():
    # Veri tabanı erişimi için gerekli kütüphaneleri import ediyoruz
    import pandas as pd
    
    # Veri tabanından verileri okuyuyoruz
    data = pd.read_csv('veriler.csv')
    
    # İstenilen veriyi seçiyoruz
    istenen_veri = data['neredeyim']
    
    # Sonuçları ekrana yazdırıyoruz
    print("SONUÇ:", istenen_veri)

# Fonksiyonu çağırıyoruz
neredeyim()