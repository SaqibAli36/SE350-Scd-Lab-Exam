import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get Supabase credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase = create_client(url, key)

# Test the connection
try:
    response = supabase.auth.get_user()
    print("✅ Connected to Supabase successfully!")
except Exception as e:
    print(f"❌ Failed to connect to Supabase: {e}")
