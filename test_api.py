import os
import time
from huggingface_hub import InferenceClient
from pydub import AudioSegment

token = "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"
model = "openai/whisper-large-v3-turbo"
client = InferenceClient(model=model, token=token)

print("Creating dummy audio...")
silence = AudioSegment.silent(duration=1000) 
silence.export("test.mp3", format="mp3")

print("Sending to API...")
try:
    res = client.automatic_speech_recognition("test.mp3")
    print("Result:", res)
except Exception as e:
    print("Exception during API call:", type(e), str(e))
