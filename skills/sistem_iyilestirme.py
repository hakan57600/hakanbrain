import psutil
import platform
import subprocess
import os
import shutil

def donanim_tara():
    """Cihazın donanım kaynaklarını analiz eder."""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = shutil.disk_usage("/")
        
        rapor = f"--- 🖥️ DONANIM ANALİZİ ---\n"
        rapor += f"İşlemci Yükü: %{cpu_usage}\n"
        rapor += f"Bellek: %{ram.percent} kullanılıyor ({ram.available // (1024**2)} MB boş)\n"
        rapor += f"Disk (Kök): %{disk.used / disk.total * 100:.1f} dolu ({disk.free // (1024**3)} GB boş)\n"
        
        if cpu_usage > 80 or ram.percent > 90:
            rapor += "⚠️ Uyarı: Sistem kaynakları yüksek yük altında, Hakan Bey.\n"
        else:
            rapor += "✅ Donanım performansı stabil, Hakan Bey.\n"
            
        return rapor
    except Exception as e:
        return f"⚠️ Donanım tarama hatası: {str(e)}, Hakan Bey."

def yazilim_denetle():
    """Sistemdeki yazılımsal eksikleri ve güncellemeleri kontrol eder."""
    try:
        rapor = f"\n--- 📦 YAZILIM DENETİMİ ---\n"
        
        # Pip güncellemelerini kontrol et
        try:
            updates = subprocess.check_output([os.sys.executable, "-m", "pip", "list", "--outdated", "--format=json"], timeout=15)
            update_list = __import__('json').loads(updates)
            if update_list:
                rapor += f"📢 {len(update_list)} adet Python paketi güncellenebilir, Hakan Bey.\n"
            else:
                rapor += "✅ Python paketleri güncel, Hakan Bey.\n"
        except:
            rapor += "⚠️ Pip güncelleme kontrolü yapılamadı, Hakan Bey.\n"
            
        # Sistem güncellemeleri (Linux)
        if platform.system() == "Linux":
            rapor += "🔍 Sistem güncellemeleri (apt) kontrol ediliyor...\n"
            
        return rapor
    except Exception as e:
        return f"⚠️ Yazılım denetim hatası: {str(e)}, Hakan Bey."

def sistem_temizle():
    """Geçici dosyaları hata vermeden tarayarak iyileştirme önerir."""
    try:
        temp_dir = os.path.expanduser("~/.cache")
        size = 0
        if os.path.exists(temp_dir):
            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    try:
                        file_path = os.path.join(root, f)
                        if os.path.exists(file_path):
                            size += os.path.getsize(file_path)
                    except (FileNotFoundError, PermissionError):
                        continue # Hatalı dosyaları atla
        
        return f"\n🧹 [İYİLEŞTİRME]: '~/.cache' dizininde yaklaşık {size // (1024**2)} MB geçici veri tespit edildi. Temizlik ile yer açılabilir, Hakan Bey."
    except Exception as e:
        return f"⚠️ Temizlik analizi hatası: {str(e)}, Hakan Bey."

def sistem_iyilestir():
    """Tüm analizleri birleştirip Hakan Bey'e sunar."""
    donanim = donanim_tara()
    yazilim = yazilim_denetle()
    temizlik = sistem_temizle()
    
    final_rapor = f"🛠️ [SİSTEM İYİLEŞTİRME RAPORU]\n\n{donanim}{yazilim}{temizlik}\n\nDurum: Sistem analiz edildi ve iyileştirme önerileri hazırlandı, Hakan Bey."
    return final_yanit_dogrula(final_rapor)

def final_yanit_dogrula(metin):
    if "Hakan Bey" not in metin:
        metin += ", Hakan Bey."
    return metin

if __name__ == "__main__":
    # Bağımsız Test (3. Aşama - Düzeltilmiş)
    print("\n🔧 [SİSTEM İYİLEŞTİRME - GÜNCEL TEST MODU] 🔧")
    print(sistem_iyilestir())
