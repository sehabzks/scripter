# 🎤 Dictation - Türkçe Ses Tanıma Sistemi

Whisper, Vosk ve Wav2Vec2 modellerini destekleyen, web tabanlı Türkçe ses tanıma (speech-to-text) uygulaması.

## ✨ Özellikler

- 🤖 **3 Farklı Model Desteği:**
  - **Whisper** (OpenAI) - Yüksek doğruluk
  - **Vosk** - Hızlı ve hafif
  - **Wav2Vec2** - Türkçe için optimize edilmiş

- 📁 **Dosya Yükleme:** WAV, MP3, MP4 formatlarını destekler
- 🔗 **YouTube Desteği:** Doğrudan YouTube linkinden çeviri
- 💾 **Bellek Optimizasyonu:** Büyük dosyalar için optimize edilmiş
- 🌐 **Web Arayüzü:** Kullanımı kolay modern arayüz

## 🚀 Kurulum

### 1. Gereksinimleri Yükle

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows için
pip install -r requirements.txt
```

### 2. Modelleri İndir

#### Vosk Modeli
```bash
python download_vosk.py
```
#### Wav2Vec2 Modeli
```bash
python download_wav2vec2.py
```

> **Not:** Whisper modeli ilk kullanımda otomatik olarak indirilir.

### 3. Uygulamayı Başlat

```bash
python app.py
```

Tarayıcıda açın: `http://localhost:5000`

## 📋 Gereksinimler

- Python 3.8+
- FFmpeg (otomatik kurulur)
- En az 8GB RAM (önerilir)
- İsteğe bağlı: CUDA destekli GPU

## 🎯 Kullanım

1. **Model Seçin:** Whisper, Vosk veya Wav2Vec2
2. **Ses Kaynağı Seçin:**
   - Dosya yükle (WAV, MP3, MP4)
   - YouTube linki gir
3. **Çevir butonuna tıklayın**
4. **Sonucu kopyalayın**

## 🔧 Model Yolu Ayarları

Modeller varsayılan olarak `D:\AI_Models_Lite` dizinine indirilir. Değiştirmek için `app.py` dosyasını düzenleyin:

```python
VOSK_MODEL_PATH = r"D:\AI_Models_Lite\vosk-model-small-tr-0.3"
WAV2VEC2_MODEL_PATH = r"D:\AI_Models_Lite\wav2vec2-turkish"
```

## 🐛 Sorun Giderme

### Whisper ile YouTube çevirisi donuyor
- Daha kısa videolar kullanın (10 dakikadan az)
- CPU kullanıyorsanız, Vosk veya Wav2Vec2 tercih edin

### Model yüklenemedi hatası
- İlgili indirme scriptini çalıştırın (`download_vosk.py` veya `download_wav2vec2.py`)
- Model yollarını kontrol edin

### Bellek sorunu
- Daha küçük dosyalar kullanın
- Vosk modelini tercih edin (en hafif)

## 📦 Teknolojiler

- **Backend:** Flask, PyTorch
- **AI Modeller:** Whisper, Vosk, Wav2Vec2
- **Audio:** librosa, soundfile, FFmpeg
- **YouTube:** yt-dlp

## 📝 Lisans

MIT

## 👨‍💻 Geliştirici

[sehabzks](https://github.com/sehabzks)

---

⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!
