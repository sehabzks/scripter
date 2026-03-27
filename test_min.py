import requests
import os
import glob
from config import Config
import static_ffmpeg
static_ffmpeg.add_paths()

def test_minimal():
    token = Config.HF_API_TOKEN
    model = Config.MODEL_NAME
    files_list = glob.glob('uploads/*.mp3') + glob.glob('uploads/*.wav')
    if not files_list: return
    with open(files_list[0], "rb") as f:
        # Use a real 5-second chunk exported properly
        from pydub import AudioSegment
        audio = AudioSegment.from_file(files_list[0])
        chunk = audio[0:5000] # 5 seconds
        chunk.export("test_chunk.mp3", format="mp3")
        with open("test_chunk.mp3", "rb") as cf:
            data = cf.read()
    
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "huggingface-hub/0.29.1; python/3.13.2; hf_hub_utils/0.29.1",
        "Content-Type": "audio/mpeg"
    }
    
    print(f"Testing multipart POST with 5s chunk to: {url}")
    files = {'file': ('audio.mp3', data, 'audio/mpeg')}
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "User-Agent": "huggingface-hub/0.29.1"},
        files=files,
        data={"return_timestamps": "true", "task": "transcribe"}
    )
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"  SUCCESS! Body: {str(resp.json())[:300]}")
    else:
        print(f"  FAILED. Body: {resp.text[:200]}")





if __name__ == "__main__":
    test_minimal()
