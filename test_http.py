import requests
import os
import glob
from config import Config

token = Config.HF_API_TOKEN
model = Config.MODEL_NAME
api_url = f"https://api-inference.huggingface.co/models/{model}"
headers = {"Authorization": f"Bearer {token}"}

files = glob.glob('uploads/*.mp3') + glob.glob('uploads/*.wav') + glob.glob('uploads/*.m4a')
if not files:
    print('No audio files found in uploads/')
else:
    f_path = files[0]
    print(f'Testing with: {f_path}')
    with open(f_path, "rb") as f:
        data = f.read()
        
    print(f'Sending {len(data)} bytes to {api_url}')
    resp = requests.post(
        api_url,
        headers={**headers, "Content-Type": "audio/mpeg"},
        data=data,
        params={"return_timestamps": "true"}
    )
    
    print(f'Status: {resp.status_code}')
    try:
        res_json = resp.json()
        print('Response JSON keys:', res_json.keys() if isinstance(res_json, dict) else type(res_json))
        print('Text:', res_json.get('text')[:100] if isinstance(res_json, dict) and res_json.get('text') else 'None')
        print('Chunks:', len(res_json.get('chunks', [])) if isinstance(res_json, dict) else 'N/A')
    except:
        print('Response is not JSON:', resp.text[:200])
