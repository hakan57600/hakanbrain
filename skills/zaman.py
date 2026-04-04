import datetime

def zaman():
    try:
        saat = datetime.datetime.now().strftime("%H:%M")
        tarih = datetime.datetime.now().strftime("%d/%m/%Y")
        
        print(f"Hakan Bey, şu anki saat {saat} ve tarih {tarih}.")
    
    except Exception as hata:
        print("Bir hata oluştu:", str(hata))

zaman()