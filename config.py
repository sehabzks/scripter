import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sestanima_gizli_anahtar_degistir_lutfen')
    UPLOAD_FOLDER = 'uploads'
    
    # Supabase Settings
    SUPABASE_URL = "https://tyamrsgxeqwtwqvbbjfl.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5YW1yc2d4ZXF3dHdxdmJiamZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM0MjU1NDEsImV4cCI6MjA4OTAwMTU0MX0.mYuFbgnz8CmNO2PrHz2Q7o6qxZD2qWCm9Yhln1BNR3s"
    
    # Hugging Face Settings
    HF_API_TOKEN = os.environ.get("HF_API_TOKEN", "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")
    MODEL_NAME = "openai/whisper-large-v3-turbo"
    # Credits
    UNLIMITED_CREDITS = True
