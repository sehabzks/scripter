from services import get_supabase_client
from config import Config
import json

def debug_db():
    print("--- Database Debug ---")
    client = get_supabase_client()
    
    # 1. Check if columns exist
    try:
        # We try to select from the table and see the column names
        res = client.table('transcriptions').select('*').limit(1).execute()
        if res.data:
            print(f"Row found! Columns: {res.data[0].keys()}")
        else:
            print("No rows in transcriptions table.")
            # Let's try to query the schema if possible (postgres catalog)
            print("Checking schema via query...")
            query_res = client.rpc('get_table_columns', {'table_name': 'transcriptions'}).execute()
            print(f"Columns info: {query_res.data}")
    except Exception as e:
        print(f"Query failed: {e}")

    # 2. Try a test insert (manual) - we'll need a real user ID or fake UUID
    # For now let's just check the column presence via error messages
    try:
        client.table('transcriptions').insert({"invalid_column_test": "val"}).execute()
    except Exception as e:
        print(f"Insert test (expected fail): {e}")

if __name__ == "__main__":
    debug_db()
