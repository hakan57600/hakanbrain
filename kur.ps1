# HAKAN BRAIN - WINDOWS AKILLI KURULUM
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "   HAKAN BRAIN v8.7 WINDOWS CORE          " -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan

# 1. Python Kontrolü
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Python bulunamadı. Microsoft Store üzerinden kuruluyor..." -ForegroundColor Yellow
    winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
} else {
    Write-Host "[ok] Python tespit edildi." -ForegroundColor Green
}

# 2. Git Kontrolü
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Git bulunamadı. Kuruluyor..." -ForegroundColor Yellow
    winget install Git.Git --accept-package-agreements --accept-source-agreements
} else {
    Write-Host "[ok] Git tespit edildi." -ForegroundColor Green
}

# 3. Proje Klonlama
if (!(Test-Path "hakanbrain")) {
    Write-Host "[+] Proje indiriliyor..." -ForegroundColor Cyan
    git clone https://github.com/hakan57600/hakanbrain.git
    Set-Location hakanbrain
} else {
    Write-Host "[+] Mevcut klasöre giriliyor..." -ForegroundColor Cyan
    Set-Location hakanbrain
    git pull
}

# 4. Bağımlılıklar
Write-Host "[+] Kütüphaneler yükleniyor..." -ForegroundColor Cyan
pip install requests psutil

# 5. Ayar Dosyası
if (!(Test-Path "config.json")) {
    $config = '{
    "GITHUB_TOKEN": "BURAYA_GITHUB_TOKEN_GIRIN",
    "GITHUB_REPO": "hakan57600/hakanbrain",
    "GROQ_API_KEY": "BURAYA_ANAHTAR_GIRIN",
    "DEVICE_NAME": "Windows PC"
}'
    $config | Out-File -FilePath "config.json" -Encoding utf8
}

Write-Host "------------------------------------------" -ForegroundColor Green
Write-Host "   KURULUM TAMAM! 'python kollar.py' yazın" -ForegroundColor Green
Write-Host "------------------------------------------" -ForegroundColor Green
