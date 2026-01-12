import os

from dotenv import load_dotenv
from supabase import AsyncClient, acreate_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")


if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in environment variables")


async def get_supabase_client():
    try:
        # Create the client
        supabase: AsyncClient = await acreate_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase client created successfully.")

        # Perform a test query (e.g., fetch the first 10 rows of a table named 'todos')
        # Make sure 'todos' table exists and RLS allows reading (or use service_role key)
        response = await supabase.table("batch").select("*").limit(1).execute()

        if response.data is not None:
            print("Successfully connected to Supabase API and fetched data.")
            print(f"Data received: {response.data}")
        else:
            print(
                "Connected to Supabase, but query returned no data (check RLS or table content)."
            )

    except Exception as e:
        print(f"Failed to connect to Supabase or execute query: {e}")
        print("Please check your network connection, URL, API key, and RLS policies.")

    finally:
        return supabase
