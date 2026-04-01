# Resmi, hafif bir Python sürümü seçiyoruz
FROM python:3.13-slim

# Uygulamanın çalışacağı klasörü ayarlıyoruz
WORKDIR /app

# İşletim sistemini güncelleyip gerekli olan ffmpeg aracını sunucuya kuruyoruz
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Gerekli kütüphane listesini kopyalıyoruz
COPY requirements.txt .

# Kütüphaneleri kuruyoruz
RUN pip install --no-cache-dir -r requirements.txt

# Projenizdeki diğer tüm kod dosyalarını kopyalıyoruz
COPY . .

# Sunucunun dışarıyla iletişim kuracağı port tanımlaması
EXPOSE 10000

# Container (Kutu) sunucuda başlatıldığında Gunicorn ile uygulamayı ayağa kaldıran son komut
# Hugging Face modelleri yavaş dönebileceği için timeout 120 sn yapıldı
CMD gunicorn app:app -b 0.0.0.0:${PORT:-10000} --workers 2 --timeout 120
