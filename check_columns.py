from services import get_supabase_client
import json

def check_columns():
    client = get_supabase_client()
    try:
        # Try to select the specific column to see if it causes an error
        print("Checking for 'chunks_json' column...")
        res = client.table('transcriptions').select('chunks_json').limit(1).execute()
        print("SUCCESS: chunks_json column exists.")
    except Exception as e:
        print(f"ERROR: chunks_json column might be missing. Error: {e}")

    try:
        print("\nChecking for 'transcribed_text' column...")
        res = client.table('transcriptions').select('transcribed_text').limit(1).execute()
        print("SUCCESS: transcribed_text column exists.")
    except Exception as e:
        print(f"ERROR: transcribed_text column missing. Error: {e}")

if __name__ == "__main__":
    check_columns()
