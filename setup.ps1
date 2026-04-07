$ErrorActionPreference = "Stop"

Write-Host "🌍 HW (HAKAN WORLD) - WINDOWS EVRENSEL KURULUMCU V1.0" -ForegroundColor Cyan
Write-Host "----------------------------------------------------"

# 1. Token Kontrolü
if (-not $env:GH_TOKEN) {
    Write-Host "⚠️ GITHUB_TOKEN eksik. Lütfen kurulum komutunu şu şekilde çalıştırın:" -ForegroundColor Yellow
    Write-Host "`$env:GH_TOKEN='token_buraya'; iwr -useb https://raw.githubusercontent.com/hakan57600/hakanbrain/main/setup.ps1 | iex"
    exit
}

# 2. Python ve Git Kontrolü
Write-Host "📦 Bağımlılıklar denetleniyor..." -ForegroundColor Gray
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python bulunamadı! Lütfen https://python.org adresinden kurun veya 'winget install python' komutunu deneyin." -ForegroundColor Red
    exit
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git bulunamadı! 'winget install git.git' komutuyla kurabilirsiniz." -ForegroundColor Red
    exit
}

# 3. Kütüphane Kurulumu
Write-Host "📦 Kütüphaneler kuruluyor..." -ForegroundColor Gray
python -m pip install requests duckduckgo-search --quiet

# 4. Depo Klonlama
$targetDir = "$HOME\hakanbrain"
if (-not (Test-Path "$targetDir\.git")) {
    Write-Host "📡 Depo klonlanıyor..." -ForegroundColor Gray
    git clone "https://hakan57600:$($env:GH_TOKEN)@github.com/hakan57600/hakanbrain.git" "$targetDir"
}

# 5. 'hw' Komutunu Mühürle
$binDir = "$HOME\AppData\Local\Microsoft\WindowsApps"
$hwBatch = "$binDir\hw.bat"

Write-Host "🔑 'hw' komutu mühürleniyor: $hwBatch" -ForegroundColor Gray
"@echo off
set GH_TOKEN=$($env:GH_TOKEN)
python `"$targetDir\brain.py`" %*
" | Out-File -FilePath $hwBatch -Encoding ascii

Write-Host "----------------------------------------------------"
Write-Host "🎉 Kurulum Tamamlandı, Hakan! Artık herhangi bir terminalde 'hw' yazabilirsin." -ForegroundColor Green
