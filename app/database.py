from supabase import acreate_client, create_client
from app.config import settings

_async_client = None
_sync_client = None


async def get_db():
    global _async_client
    if _async_client is None:
        _async_client = await acreate_client(
            settings.supabase_url,
            settings.supabase_key
        )
    return _async_client


def get_supabase_sync():
    global _sync_client
    if _sync_client is None:
        _sync_client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    return _sync_client