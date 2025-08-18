# app/jobs/expire.py
import asyncio, logging
from datetime import datetime
from app.config import load_settings
from app.storage import Session, User
from app.outline_api import OutlineAPI

log = logging.getLogger("expire")

async def revoke_expired_once(bot=None):
    s = load_settings()
    now = datetime.utcnow()
    to_revoke = []

    with Session() as db:
        users = (
            db.query(User)
            .filter(User.expires_at != None)  # noqa
            .all()
        )
        for u in users:
            if u.expires_at and u.expires_at < now and u.current_key_id:
                to_revoke.append((u.tg_id, u.current_key_id))

    if not to_revoke:
        return

    api = OutlineAPI(s.outline_api_url, s.outline_api_key)
    for tg_id, key_id in to_revoke:
        try:
            await api.delete_key(key_id)
            with Session() as db:
                u = db.query(User).filter_by(tg_id=tg_id).one_or_none()
                if u:
                    u.current_key_id = None
                    u.current_key_secret = None
                    db.commit()
            log.info("Revoked expired key for tg_id=%s", tg_id)
            if bot:
                try:
                    await bot.send_message(
                        chat_id=tg_id,
                        text="⌛️ Срок подписки истёк. Ключ деактивирован."
                    )
                except Exception:
                    pass
        except Exception as e:
            log.error("Failed to revoke for tg_id=%s: %s", tg_id, e)

    await api.close()

async def loop_revoke_expired(bot, interval_sec: int = 90000):
    # каждые 25 часов
    while True:
        try:
            await revoke_expired_once(bot)
        except Exception as e:
            log.error("Expire loop error: %s", e)
        await asyncio.sleep(interval_sec)