import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    UPLOAD_FOLDER = 'uploads'
    
    # Supabase Settings
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Hugging Face Settings
    HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
    MODEL_NAME = "openai/whisper-large-v3-turbo"
    # Credits
    UNLIMITED_CREDITS = True
