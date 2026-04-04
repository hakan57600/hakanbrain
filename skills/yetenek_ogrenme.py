import requests
import os
import re

OLLAMA_URL = "http://localhost:11434/api/generate"

def kod_temizle(ham_kod):
    """
    LLM'den gelen yanıtı sadece saf Python koduna indirger.
    Dosya yolları, açıklamalar ve markdown bloklarını temizler.
    """
    # Markdown bloklarını temizle
    temiz_kod = re.sub(r'```python|```', '', ham_kod).strip()
    
    # Satır satır kontrol et ve sadece geçerli Python başlangıçlarını tut
    satirlar = temiz_kod.split('\n')
    gecerli_satirlar = []
    kod_basladi = False
    
    for satir in satirlar:
        # Eğer satır import, def, class veya yorum satırı ile başlıyorsa kod başlamıştır
        if re.match(r'^(import|from|def|class|#|\s+)', satir):
            kod_basladi = True
        
        if kod_basladi:
            # Dosya yolu içeren satırları (örn: skills/...) ele
            if not re.match(r'^skills/|^\|', satir):
                gecerli_satirlar.append(satir)
                
    return '\n'.join(gecerli_satirlar).strip()

def yeni_yetenek_uret(yetenek_adi, aciklama):
    """
    Hakan Bey için otonom olarak HATASIZ bir Python yetenek modülü üretir.
    """
    prompt = (
        f"Sen bir Python uzmanısın. Hakan Bey için '{yetenek_adi}' adında bir yetenek modülü yaz.\n"
        f"GÖREV: {aciklama}\n"
        "KURALLAR:\n"
        "1. SADECE SAF PYTHON KODU DÖNDÜR.\n"
        "2. Açıklama yapma, dosya yolu yazma, ağaç yapısı gösterme.\n"
        "3. Kodun içinde mutlaka Hakan Bey'e hitap et.\n"
        "4. 'try-except' blokları kullan.\n"
        "SADECE KOD."
    )

    try:
        payload = {
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0}
        }
        res = requests.post(OLLAMA_URL, json=payload, timeout=120).json()
        ham_kod = res['response'].strip()
        
        # Filtreleme yap
        temiz_kod = kod_temizle(ham_kod)
        
        if not temiz_kod:
            return "⚠️ Kod üretildi ancak temizleme filtresinden geçemedi, Hakan Bey."
            
        # Dosyayı kaydet
        dosya_adi = f"skills/{yetenek_adi.lower()}.py"
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(temiz_kod)
            
        return f"✅ '{yetenek_adi}' yeteneği arındırılarak kodlandı ve '{dosya_adi}' olarak mühürlendi, Hakan Bey."
        
    except Exception as e:
        return f"⚠️ Yetenek üretimi sırasında bir hata oluştu: {str(e)}, Hakan Bey."

if __name__ == "__main__":
    # Bağımsız Test (3. Aşama - Düzeltilmiş)
    print("\n🛠 [YETENEK ÖĞRENME - ARINDIRILMIŞ TEST MODU] 🛠")
    print(yeni_yetenek_uret("zaman", "Güncel saat ve tarihi Hakan Bey'e nazikçe raporlayan bir yetenek."))
