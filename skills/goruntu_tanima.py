import requests
import base64
import os

OLLAMA_URL = "http://localhost:11434/api/generate"

def goruntu_analiz_et(dosya_yolu, prompt="Bu görselde ne görüyorsun?"):
    """
    Hakan Bey için yerel llava modelini kullanarak görseli analiz eder.
    """
    if not os.path.exists(dosya_yolu):
        return f"⚠️ Dosya bulunamadı: {dosya_yolu}, Hakan Bey."

    try:
        # Görseli base64 formatına çevir
        with open(dosya_yolu, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        payload = {
            "model": "llava",
            "prompt": prompt + " Yanıtını Hakan Bey'e hitap ederek Türkçe ver.",
            "images": [encoded_string],
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=180).json()
        analiz = response.get('response', 'Analiz alınamadı.')
        
        return f"🖼️ [GÖRÜNTÜ ANALİZ RAPORU]\n\n{analiz}\n\nDurum: Analiz Tamamlandı, Hakan Bey."

    except Exception as e:
        return f"⚠️ Görüntü analizi sırasında bir hata oluştu: {str(e)}, Hakan Bey."

if __name__ == "__main__":
    # Bağımsız Test (3. Aşama)
    # Test için sistemdeki bir görseli (varsa) kullanabiliriz
    print("\n👁️ [GÖRÜNTÜ TANIMA - TEST MODU] 👁️")
    # Örnek test çağrısı (Dosya yolu varsa çalışır)
    # print(goruntu_analiz_et("/home/hakan/Resimler/test.jpg"))
    print("Modül hazır, test için görsel bekleniyor, Hakan Bey.")
