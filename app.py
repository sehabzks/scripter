import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from config import Config
app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register Blueprints
from routes.main import main_bp
from routes.auth import auth_bp
from routes.transcribe import transcribe_bp
from routes.history import history_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(transcribe_bp)
app.register_blueprint(history_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
