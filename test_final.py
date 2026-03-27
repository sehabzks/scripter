import requests
import os
import glob
import time
from pydub import AudioSegment
import static_ffmpeg
static_ffmpeg.add_paths()
from config import Config

def test_api():
    token = Config.HF_API_TOKEN
    model = 'openai/whisper-large-v3'
    
    files = glob.glob('uploads/*.mp3') + glob.glob('uploads/*.wav')
    if not files:
        print('No audio files found in uploads/')
        return
    
    filepath = files[0]
    print(f'Testing with: {filepath}')
    
    audio = AudioSegment.from_file(filepath)
    chunk_path = "debug_chunk.mp3"
    audio[0:10000].export(chunk_path, format="mp3") # 10s chunk
    
    print(f'Testing {model} with InferenceClient helper...')
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=token)
        
        # This is the official helper method in recent versions
        res = client.automatic_speech_recognition(
            chunk_path,
            model=model,
            return_timestamps=True
        )
        print(f'SUCCESS!')
        print(f'Text: {res.text[:100]}...')
        if hasattr(res, 'chunks') and res.chunks:
            print(f'CHUNKS FOUND: {len(res.chunks)}')
            print(f'First chunk: {res.chunks[0]}')
        else:
            print('No chunks found in response.')

    except Exception as e:
        print(f'API Call Failed: {e}')

if __name__ == "__main__":
    test_api()
