# KÖLE (hakanbrain) - Merkezi Yönetim Sistemi

Bu proje, GitHub üzerinden gönderilen görevleri yerel makinede çalıştıran ve sonuçlarını senkronize eden bir "worker" sistemidir.

## Özellikler
- **Bulut Senkronizasyonu:** Görevler ve sonuçlar GitHub üzerinden anlık senkronize edilir.
- **Güvenlik:** Sadece `allowed_commands.json` içindeki komutlar çalıştırılabilir.
- **Loglama:** Tüm işlemler `hakanbrain.log` dosyasına kaydedilir.
- **Yönetim Paneli:** `index.html` üzerinden görsel takip sağlanabilir.

## Kurulum
1. Sanal ortam oluşturun: `python3 -m venv venv`
2. Bağımlılıkları yükleyin: `pip install -r requirements.txt`
3. `config.json` dosyasını düzenleyin (GitHub Token ve Repo).
4. `kollar.py` dosyasını çalıştırın: `python3 kollar.py`

## Giriş Bilgileri
- **Kullanıcı:** hakan
- **Şifre:** 2205 (PBKDF2 ile şifrelenmiştir)
