import requests
import os
import glob
from config import Config

def probe():
    token = Config.HF_API_TOKEN
    model = 'openai/whisper-tiny'
    
    # Method 1: Standard URL
    urls = [
        f"https://api-inference.huggingface.co/models/{model}",
        f"https://api-inference.huggingface.co/pipeline/automatic-speech-recognition/{model}"
    ]
    
    files = glob.glob('uploads/*.mp3') + glob.glob('uploads/*.wav')
    if not files: return
    with open(files[0], "rb") as f:
        data = f.read()[:1000000] # 1MB for speed
        
    for url in urls:
        print(f"Testing URL: {url}")
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}", "User-Agent": "huggingface-hub/0.29.1"},
            data=data,
            params={"return_timestamps": "true"},
            allow_redirects=False # IMPORTANT
        )
        print(f"  Status: {resp.status_code}")
        print(f"  Location: {resp.headers.get('Location')}")
        if resp.status_code == 200:
            try:
                js = resp.json()
                print(f"  Success! Keys: {js.keys() if isinstance(js, dict) else type(js)}")
                if isinstance(js, dict) and "chunks" in js:
                    print("  CHUNKS FOUND!")
            except:
                print("  Not JSON")

if __name__ == "__main__":
    probe()
