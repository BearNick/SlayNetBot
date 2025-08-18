
from app.storage import Session, User, init_db
from datetime import datetime
from app.config import load_settings
from app.outline_api import OutlineAPI
import asyncio

async def clean_expired_keys():
    init_db()
    settings = load_settings()
    api = OutlineAPI(settings.outline_api_url, settings.outline_api_key)
    with Session() as s:
        now = datetime.utcnow()
        users = s.query(User).filter(User.expires_at != None).all()
        for u in users:
            if u.expires_at < now and u.current_key_id:
                try:
                    await api.delete_key(u.current_key_id)
                except Exception:
                    pass
                u.current_key_id = None
                u.current_key_secret = None
        s.commit()
    await api.close()

if __name__ == "__main__":
    asyncio.run(clean_expired_keys())
