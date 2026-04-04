skills/
|---- __init__.py
|---- hesaplama.py

skills/hesaplama.py

def hesapla(sayilar):
    try:
        ortalama = sum(sayilar) / len(sayilar)
        return f"Hakan Bey, verilen sayıların ortalaması {ortalama} dir."
    except ZeroDivisionError:
        return "Hakan Bey, liste boş olamaz!"
    except TypeError:
        return "Hakan Bey, listede sadece sayılar olabilir!"

def raporla(sayilar):
    try:
        ortalama = hesapla(sayilar)
        return f"Hesaplamalar:\n{ortalama}"
    except Exception as e:
        return f"Hata: {str(e)}"


skills/__init__.py

# Boş dosya, sadece dizin oluşturmak için kullanılır.