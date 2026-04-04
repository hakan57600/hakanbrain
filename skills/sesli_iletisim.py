import pyttsx3

def sesli_oku(metin):
    """
    Hakan Bey için metni kararlı ve hatasız bir şekilde seslendirir.
    """
    try:
        engine = pyttsx3.init()
        # Ses hızı ve tonu ayarları (Daha doğal bir hitap için)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        
        # Sesli oku ve bekle (Hataları önlemek için)
        engine.say(metin)
        engine.runAndWait()
        
        # Bellek temizliği (Zayıf referans hatalarını önlemek için)
        del engine
        return f"Hakan Bey için sesli okuma tamamlandı."
        
    except Exception as e:
        return f"⚠️ Sesli iletişim hatası: {str(e)}, Hakan Bey."

if __name__ == "__main__":
    # Bağımsız Test
    print(sesli_oku("Hakan Bey, sesli iletişim sistemimiz kararlı hale getirildi."))
