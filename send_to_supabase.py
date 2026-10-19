import os
from supabase import create_client, Client

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

supabase: Client = create_client(url, key)


data = {
    "punch_type": "jab",
    "punch_hand": "left",
    "impact_force": 325.5,
    "punch_velocity": 13.8
}

result = supabase.table("punches").insert(data).execute()
print("✅ Data sent:", result)
