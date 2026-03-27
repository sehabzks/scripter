from huggingface_hub import InferenceClient
import glob

token = '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'
model = 'openai/whisper-large-v3-turbo'
client = InferenceClient(model=model, token=token)

files = glob.glob('uploads/*.mp3') + glob.glob('uploads/*.wav') + glob.glob('uploads/*.m4a')
if not files:
    print('Uploads klasorunde ses dosyasi bulunamadi.')
else:
    f = files[0]
    print(f'Test dosyasi: {f}')
    result = client.automatic_speech_recognition(f, return_timestamps=True)
    print('result type:', type(result))
    print('result.text:', (result.text or '')[:120])
    print('has chunks attr:', hasattr(result, 'chunks'))
    chunks = getattr(result, 'chunks', None)
    print('chunks:', chunks[:3] if chunks else 'None/Empty')
