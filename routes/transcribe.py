import os
import subprocess
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from pydub import AudioSegment
from services import get_user_supabase, query_huggingface_api, download_youtube_audio

transcribe_bp = Blueprint('transcribe', __name__)

@transcribe_bp.route('/transcribe', methods=['POST'])
def transcribe():
    if 'user_id' not in session:
        return jsonify({'error': 'Oturum süresi doldu, lütfen giriş yapın.'}), 401

    file = request.files.get('file')
    youtube_url = request.form.get('url')
    local_filepath = request.form.get('filepath')
    
    filepath = None
    created_temp_file = False
    
    try:
        # 1. Dosya Kaynağını Belirle ve Ayarla
        if youtube_url and youtube_url.strip() != "":
            print(f"Processing YouTube URL: {youtube_url}")
            try:
                filepath = download_youtube_audio(youtube_url)
                created_temp_file = True
            except Exception as e:
                return jsonify({'error': f"YouTube indirme hatası: {str(e)}"}), 500

        elif local_filepath and local_filepath.strip() != "":
            lp = local_filepath.strip().strip('"').strip("'")
            if not os.path.exists(lp):
                return jsonify({'error': f"Dosya bulunamadı: {lp}"}), 400
                
            video_exts = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg'}
            ext = os.path.splitext(lp)[1].lower()
            if ext in video_exts:
                print(f"Video dosyası tespit edildi, MP3'e çevriliyor: {lp}") 
                temp_audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_video_audio.mp3')
                result = subprocess.run(
                    ['ffmpeg', '-y', '-i', lp, '-ac', '1', '-ar', '16000', '-b:a', '32k', '-vn', temp_audio_path],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    return jsonify({'error': f"Video ses çıkarma hatası: {result.stderr[-500:]}"}), 500
                filepath = temp_audio_path
                created_temp_file = True
            else:
                filepath = lp
                created_temp_file = False

        elif file and file.filename != '':
            filename = secure_filename(file.filename)
            video_exts = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg'}
            ext = os.path.splitext(filename)[1].lower()
            saved_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(saved_path)
            
            if ext in video_exts:
                print(f"Yüklenen video dosyasından ses çıkarılıyor: {filename}")
                temp_audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_upload_audio.mp3')
                result = subprocess.run(
                    ['ffmpeg', '-y', '-i', saved_path, '-ac', '1', '-ar', '16000', '-b:a', '32k', '-vn', temp_audio_path],
                    capture_output=True, text=True
                )
                os.remove(saved_path)
                if result.returncode != 0:
                    return jsonify({'error': f"Video ses çıkarma hatası: {result.stderr[-500:]}"}), 500
                filepath = temp_audio_path
            else:
                filepath = saved_path
            created_temp_file = True
        else:
            return jsonify({'error': 'Dosya, dosya yolu veya YouTube linki gerekli'}), 400

        # ---- KREDİ KONTROLÜ ----
        try:
            audio = AudioSegment.from_file(filepath)
            duration_seconds = int(len(audio) / 1000)
            
            user_client = get_user_supabase(session.get('access_token'))
            
            # Sınırsız kredi modu aktif değilse kontrol et
            if not current_app.config.get('UNLIMITED_CREDITS', False):
                credit_res = user_client.table('user_credits').select('credits_seconds').eq('user_id', session['user_id']).execute()
                
                if not credit_res.data:
                    return jsonify({'error': 'Sunucu tarafında kredi bilginiz bulunamadı, hesabınızı kontrol edin.'}), 402
                    
                current_credits = credit_res.data[0]['credits_seconds']
                if current_credits < duration_seconds:
                    return jsonify({'error': f'Yetersiz kredi! Bu işlem ({duration_seconds} sn) için yeterli krediniz ({current_credits} sn) yok.'}), 402
            else:
                print("Sınırsız kredi modu aktif - Kredi kontrolü atlanıyor.")
                current_credits = 999999 # Geçici değer
        except Exception as ce:
            print("Kredi doğrulama hatası:", ce)
            return jsonify({'error': 'Kredi bilgileri doğrulanırken bir hata oluştu.'}), 500

        # 2. Hugging Face API'ye Gönder
        api_result = query_huggingface_api(filepath)
        
        # 3. Geçici Dosyaları Temizle
        if created_temp_file and filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass
                
        # 4. Yanıtı Döndür
        if "error" in api_result:
            return jsonify(api_result), 500
            
        transcribed_text = api_result.get("text", "")
        timed_chunks = api_result.get("chunks", [])

        # 5. İşlem Başarılı: Bakiyeden Düş ve Geçmişe Ekle
        try:
            is_unlimited = current_app.config.get('UNLIMITED_CREDITS', False)
            new_credits = current_credits if is_unlimited else current_credits - duration_seconds
            
            # 5a. Krediyi Güncelle (Sınırsız değilse)
            if not is_unlimited:
                user_client.table('user_credits').update({'credits_seconds': new_credits}).eq('user_id', session['user_id']).execute()
            
            # 5b. Çeviriyi Veritabanına Kaydet
            print(f"Veritabani kaydi baslatiliyor... User: {session['user_id']}")
            import json as _json
            source_name = youtube_url if youtube_url else (local_filepath if local_filepath else (file.filename if file else "Unknown Source"))
            
            db_res = user_client.table('transcriptions').insert({
                "user_id": session['user_id'],
                "filename_or_url": source_name,
                "duration_seconds": duration_seconds,
                "transcribed_text": transcribed_text,
                "chunks_json": _json.dumps(timed_chunks, ensure_ascii=False)
            }).execute()
            
            if hasattr(db_res, 'data') and db_res.data:
                print(f"Veritabani kaydi basarili ID: {db_res.data[0].get('id')}")
            else:
                print(f"VERITABANI KAYDI BOS DONDU: {db_res}")
                
        except Exception as de:
            print(f"!!! KRITIK VERITABANI HATASI: {de}")
            # Opsiyonel: Flask loglarina da yaz
            import traceback
            traceback.print_exc()
            new_credits = current_credits

        # chunks with real timestamps for SRT on main page
        frontend_chunks = timed_chunks if timed_chunks else [{'start': 0, 'end': duration_seconds, 'text': transcribed_text}]

        return jsonify({
            'text': transcribed_text,
            'chunks': frontend_chunks,
            'new_credits_seconds': 999999 if current_app.config.get('UNLIMITED_CREDITS', False) else new_credits
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
