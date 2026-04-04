import os
import ast
import json
import subprocess
import shutil

MEMORY_FILE = os.path.expanduser("~/hakan_memory.json")
SKILLS_DIR = "skills"

def kod_temizle():
    """Skills dizinindeki hatalı (SyntaxError) kodları tespit eder."""
    hatali_dosyalar = []
    rapor = "--- 🛠️ KOD DENETİMİ ---\n"
    
    for dosya in os.listdir(SKILLS_DIR):
        if dosya.endswith(".py"):
            yol = os.path.join(SKILLS_DIR, dosya)
            try:
                with open(yol, "r", encoding="utf-8") as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                hatali_dosyalar.append(f"{dosya} (Satır: {e.lineno})")
    
    if hatali_dosyalar:
        rapor += f"⚠️ Hatalı kodlar tespit edildi: {', '.join(hatali_dosyalar)}, Hakan Bey.\n"
    else:
        rapor += "✅ Tüm kodlar hatasız ve temiz, Hakan Bey.\n"
    
    return rapor

def hafiza_temizle():
    """Hafızadaki bozuk veya gereksiz verileri arındırır."""
    rapor = "\n--- 🧠 HAFIZA ARINDIRMA ---\n"
    if not os.path.exists(MEMORY_FILE):
        return rapor + "⚠️ Hafıza dosyası bulunamadı, Hakan Bey."

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        degisiklik = False
        # Boş kategorileri veya yinelenen verileri temizle
        if "hakan_profili" in data:
            for kat, veriler in list(data["hakan_profili"].items()):
                if not veriler:
                    del data["hakan_profili"][kat]
                    degisiklik = True
                elif isinstance(veriler, list):
                    ozgun_veriler = list(set(veriler))
                    if len(ozgun_veriler) != len(veriler):
                        data["hakan_profili"][kat] = ozgun_veriler
                        degisiklik = True
        
        if degisiklik:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            rapor += "🧹 Hafızadaki gereksiz veriler temizlendi, Hakan Bey.\n"
        else:
            rapor += "✅ Hafıza tertemiz ve düzenli, Hakan Bey.\n"
            
        return rapor
    except Exception as e:
        return rapor + f"⚠️ Hafıza temizleme hatası: {str(e)}, Hakan Bey."

def yukleme_temizle():
    """Bozuk paketleri ve sistemdeki gereksiz derleme dosyalarını siler."""
    rapor = "\n--- 📦 YÜKLEME TEMİZLİĞİ ---\n"
    try:
        # Gereksiz __pycache__ dizinlerini temizle
        temizlenen_cache = 0
        for root, dirs, files in os.walk("."):
            if "__pycache__" in dirs:
                shutil.rmtree(os.path.join(root, "__pycache__"))
                temizlenen_cache += 1
        
        if temizlenen_cache > 0:
            rapor += f"🧹 {temizlenen_cache} adet __pycache__ dizini temizlendi, Hakan Bey.\n"
        
        # Pip bozuk paket kontrolü
        try:
            res = subprocess.run(["pip", "check"], capture_output=True, text=True, timeout=15)
            if res.returncode != 0:
                rapor += f"⚠️ Bozuk paketler bulundu: {res.stdout.strip()}, Hakan Bey.\n"
            else:
                rapor += "✅ Tüm yazılım yüklemeleri sağlıklı, Hakan Bey.\n"
        except:
            rapor += "⚠️ Paket denetimi yapılamadı, Hakan Bey.\n"
            
        return rapor
    except Exception as e:
        return rapor + f"⚠️ Yükleme temizleme hatası: {str(e)}, Hakan Bey."

def sistem_oz_arindirma():
    """Tüm temizlik işlemlerini birleştirir."""
    k = kod_temizle()
    h = hafiza_temizle()
    y = yukleme_temizle()
    
    final_rapor = f"🧹 [TEMİZLİKÇİ RAPORU]\n\n{k}{h}{y}\n\nDurum: HW sistemi öz-arındırma döngüsünü tamamladı, Hakan Bey."
    return final_rapor

if __name__ == "__main__":
    # Bağımsız Test (3. Aşama)
    print("\n🧼 [TEMİZLİKÇİ - TEST MODU] 🧼")
    print(sistem_oz_arindirma())
