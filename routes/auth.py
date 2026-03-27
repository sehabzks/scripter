from flask import Blueprint, render_template, request, session, redirect, url_for
from services import get_supabase_client

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            client = get_supabase_client()
            res = client.auth.sign_in_with_password({"email": email, "password": password})
            session['user_id'] = res.user.id
            session['access_token'] = res.session.access_token
            return redirect(url_for('main.index'))
        except Exception as e:
            msg = str(e)
            if "AuthApiError" in msg:
                msg = "Giriş bilgileri hatalı."
            return render_template('login.html', error=msg)
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            client = get_supabase_client()
            res = client.auth.sign_up({"email": email, "password": password})
            if res.user:
                # If email confirmation is enabled on Supabase, res.session will be None.
                if res.session:
                    session['user_id'] = res.user.id
                    session['access_token'] = res.session.access_token
                    return redirect(url_for('main.index'))
                else:
                    return render_template('login.html', error="Kayıt başarılı! Lütfen E-Postanızı doğrulayıp giriş yapın.")
            else:
                return render_template('register.html', error="Kayıt olunamadı.")
        except Exception as e:
            msg = str(e)
            if "AuthApiError" in msg or "already" in msg.lower():
                msg = "Kayıt hatası veya bu E-Posta zaten kullanımda."
            return render_template('register.html', error=msg)
    return render_template('register.html')

@auth_bp.route('/google_login')
def google_login():
    try:
        client = get_supabase_client()
        # redirect_to parameter defines where Supabase will send the user back after Google auth
        # In a local development environment, use the local address. In prod this must be updated.
        res = client.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": request.url_root + "auth/callback"
            }
        })
        return redirect(res.url)
    except Exception as e:
        return render_template('login.html', error=f"Google giriş hatası: {str(e)}")

@auth_bp.route('/auth/callback')
def auth_callback():
    # Supabase returns the session token as a hash fragment (#access_token=...), 
    # which cannot be read by Flask directly on the server side because hash fragments are not sent to the server.
    # Therefore, we render a minimal HTML page that uses JS to extract the tokens and send them back to the server.
    return """
    <html><body>
    <script>
      const hash = window.location.hash.substring(1);
      const params = new URLSearchParams(hash);
      const accessToken = params.get('access_token');
      
      if (accessToken) {
          // POST the token to our server counterpart
          fetch('/auth/set_session', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ access_token: accessToken })
          }).then(res => {
              window.location.href = '/';
          });
      } else {
          window.location.href = '/login';
      }
    </script>
    </body></html>
    """

@auth_bp.route('/auth/set_session', methods=['POST'])
def set_session():
    data = request.json
    access_token = data.get('access_token')
    if access_token:
        try:
            client = get_supabase_client()
            res = client.auth.get_user(access_token)
            if res and res.user:
                session['user_id'] = res.user.id
                session['access_token'] = access_token
                return jsonify({"status": "success"})
        except Exception as e:
            print(f"Error validating token: {e}")
    return jsonify({"status": "error"}), 400

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
