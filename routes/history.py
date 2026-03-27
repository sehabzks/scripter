from flask import Blueprint, render_template, session, redirect, url_for
from services import get_user_supabase

history_bp = Blueprint('history', __name__)

@history_bp.route('/history/transcriptions')
def transcription_history():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    transcriptions = []
    try:
        user_client = get_user_supabase(session.get('access_token'))
        res = user_client.table('transcriptions').select('id,filename_or_url,duration_seconds,transcribed_text,chunks_json,created_at').eq('user_id', session['user_id']).order('created_at', desc=True).execute()
        transcriptions = res.data or []
    except Exception as e:
        print("Çeviri geçmişi çekilirken hata:", e)

    return render_template('history_transcriptions.html', transcriptions=transcriptions)


@history_bp.route('/history/payments')
def payment_history():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    transactions = []
    try:
        user_client = get_user_supabase(session.get('access_token'))
        res = user_client.table('transactions').select('*').eq('user_id', session['user_id']).order('created_at', desc=True).execute()
        transactions = res.data or []
    except Exception as e:
        print("Ödeme geçmişi çekilirken hata:", e)

    return render_template('history_payments.html', transactions=transactions)
