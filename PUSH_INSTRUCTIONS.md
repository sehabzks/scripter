# GitHub'a Push Etme Talimatları

## 1. GitHub'da Repository Oluştur

Antigravity'deki GitHub entegrasyonunu kullanarak:
- Repository adı: **dictation**
- Açıklama: **Türkçe ses tanıma sistemi - Turkish speech-to-text with Whisper, Vosk, and Wav2Vec2**
- Public olarak oluştur
- README, .gitignore, license ekleme (zaten var)

## 2. Repo oluşturduktan sonra bu komutları çalıştır:

```powershell
# Remote ekle (URL'i kendi repo URL'inle değiştir)
git remote add origin https://github.com/sehabzks/dictation.git

# Ana branch'i belirle
git branch -M main

# Push et
git push -u origin main
```

## Alternatif: Eğer remote zaten varsa

```powershell
# Mevcut remote'u kontrol et
git remote -v

# Varsa değiştir
git remote set-url origin https://github.com/sehabzks/dictation.git

# Push et
git push -u origin main
```

## ✅ Başarılı olduğunda

https://github.com/sehabzks/dictation adresinde projen görünecek!
