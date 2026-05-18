from supabase import acreate_client
from app.config import settings

_client = None

async def get_db() :
    global _client
    if _client is None:
        _client = await acreate_client(
            settings.supabase_url,
            settings.supabase_key
        )
    return _client