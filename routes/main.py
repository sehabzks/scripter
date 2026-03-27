from flask import Blueprint, render_template, session, redirect, url_for, current_app
from services import get_user_supabase

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    credits_seconds = 0
    is_unlimited = current_app.config.get('UNLIMITED_CREDITS', False)
    
    if not is_unlimited:
        try:
            user_client = get_user_supabase(session.get('access_token'))
            response = user_client.table('user_credits').select('credits_seconds').eq('user_id', session['user_id']).execute()
            if response.data:
                credits_seconds = response.data[0]['credits_seconds']
        except Exception as e:
            print("Kredi çekilirken hata:", e)
    else:
        credits_seconds = 999999
        
    return render_template('index.html', credits_seconds=credits_seconds, is_unlimited=is_unlimited)
