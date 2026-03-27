import os
import glob
import subprocess
import time
import yt_dlp
from pydub import AudioSegment
import static_ffmpeg
static_ffmpeg.add_paths()
from supabase import create_client
from huggingface_hub import InferenceClient
from config import Config

def get_supabase_client():
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def get_user_supabase(access_token):
    client = get_supabase_client()
    if access_token:
        client.postgrest.auth(access_token)
    return client

# --- Hugging Face Service ---
hf_client = None
if Config.HF_API_TOKEN:
    try:
        hf_client = InferenceClient(model=Config.MODEL_NAME, token=Config.HF_API_TOKEN)
    except Exception as e:
        print(f"HF Client baslatilamadi: {e}")

from pydub.silence import split_on_silence

def query_huggingface_api(filepath):
    if not hf_client:
        return {"error": "HF_API_TOKEN veya hf_client eksik."}
        
    try:
        audio = AudioSegment.from_file(filepath)
        
        # Sesi sessizliklere gore bolmek, dogal "timeline" kısımlari olusturur.
        # Bu sayede API timestamp destegi gerektirmeden gercekci SRT uretilebilir.
        print("Ses dogal sessizliklere gore bolunuyor (bu biraz zaman alabilir)...")
        chunks = split_on_silence(
            audio,
            min_silence_len=700,    # En az 0.7 saniye sessizlik
            silence_thresh=-40,    # Sessizlik esigi (dB)
            keep_silence=200       # Cumle sonlarinda hafif bosluk birak
        )
        
        # Eger cok uzun parcalar kaldiysa onlari da 10sn'lik parcalara bolelim
        final_audio_chunks = []
        for c in chunks:
            if len(c) > 10000: # 10 saniyeden uzunsa
                for i in range(0, len(c), 10000):
                    final_audio_chunks.append(c[i:i+10000])
            else:
                final_audio_chunks.append(c)
        
        if not final_audio_chunks:
            # Sessizlik bulunamadiysa veya ses cok kisa ise tek parca dondur
            final_audio_chunks = [audio]

        full_text = []
        all_timed_chunks = []
        time_offset = 0.0
        
        print(f"Toplam {len(final_audio_chunks)} parca gonderilecek... Model: {Config.MODEL_NAME}")
        
        for k, chunk in enumerate(final_audio_chunks):
            chunk_duration_sec = len(chunk) / 1000.0
            if chunk_duration_sec < 0.5: # Cok kisa parcalari atla
                time_offset += chunk_duration_sec
                continue

            chunk_path = f"{filepath}_chunk{k}.mp3"
            chunk.export(chunk_path, format="mp3", parameters=["-b:a", "32k", "-ar", "16000", "-ac", "1"])
            
            print(f"  Parca {k+1}/{len(final_audio_chunks)} gonderiliyor ({chunk_duration_sec:.1f}s)...")
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = hf_client.automatic_speech_recognition(chunk_path)
                    raw_text = (result.text or "").strip()
                    
                    if raw_text:
                        print(f"    -> ok! text: {raw_text[:30]}...")
                        full_text.append(raw_text)
                        
                        # Bu parcanin suresini srt timing olarak ekliyoruz
                        all_timed_chunks.append({
                            "start": round(time_offset, 2),
                            "end": round(time_offset + chunk_duration_sec, 2),
                            "text": raw_text
                        })
                    break
                    
                except Exception as api_err:
                    err_str = str(api_err).lower()
                    print(f"    -> HATA (deneme {attempt+1}): {api_err}")
                    if "503" in err_str or "loading" in err_str:
                        time.sleep(10)
                    else:
                        time.sleep(3)
            
            time_offset += chunk_duration_sec
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
                
        if not full_text:
            return {"error": "Cevrilen metin bulunamadi veya API hata dondurdu."}
        
        return {
            "text": " ".join(full_text),
            "chunks": all_timed_chunks
        }
            
    except Exception as e:
        return {"error": f"Islem sirasinda beklenmedik hata: {str(e)}"}

# --- Audio/YouTube Service ---
def download_youtube_audio(url):
    filename_template = os.path.join(Config.UPLOAD_FOLDER, '%(id)s.%(ext)s')

    base_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
        'retries': 3,
        'extractor_retries': 3,
    }

    cookies_txt = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies.txt')
    attempts = []
    if os.path.exists(cookies_txt):
        attempts.append(('cookies.txt', {'cookiefile': cookies_txt}))
    for browser in ['chrome', 'firefox', 'edge']:
        attempts.append((browser, {'cookiesfrombrowser': (browser,)}))
    attempts.append(('none', {}))

    last_error = None
    for label, extra_opts in attempts:
        ydl_opts = {**base_opts, **extra_opts}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info['id']
                matches = glob.glob(os.path.join(Config.UPLOAD_FOLDER, f"{video_id}*.wav"))
                if matches:
                    print(f"YouTube download successful (method={label})")
                    return matches[0]
                raise FileNotFoundError("Could not locate downloaded YouTube audio file.")
        except Exception as e:
            err_str = str(e)
            last_error = e
            print(f"YouTube attempt failed (method={label}): {e}")
            if any(k in err_str.lower() for k in ['403', 'forbidden', 'dpapi', 'decrypt', 'cookie', 'format']):
                continue
            raise

    raise last_error
