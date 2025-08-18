# app/jobs/da_watcher.py
import asyncio, time, re, json, logging
import httpx
from datetime import datetime, timedelta
from app.config import load_settings
from app.storage import Session, Payment, User, KV
from app.outline_api import OutlineAPI

log = logging.getLogger("da_watcher")
CODE_RE = re.compile(r"(SLAY-[A-Z0-9]{4,8})", re.IGNORECASE)

async def _fetch_donations(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=15.0) as cli:
        r = await cli.get(
            "https://www.donationalerts.com/api/v1/alerts/donations",
            params={"skip": 0, "limit": 50},
            headers=headers,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("data") or data.get("donations") or data.get("payload") or []

def _get_kv(key: str) -> str | None:
    with Session() as s:
        row = s.get(KV, key)
        return row.value if row else None

def _set_kv(key: str, value: str):
    with Session() as s:
        row = s.get(KV, key)
        if not row:
            s.add(KV(key=key, value=value))
        else:
            row.value = value
        s.commit()

async def process_donations(bot):
    s = load_settings()
    if not s.da_access_token:
        return

    items = []
    try:
        items = await _fetch_donations(s.da_access_token)
    except Exception as e:
        log.error("DA fetch error: %s", e)
        return
    if not items:
        return

    last_id = int((_get_kv("da_last_id") or "0") or 0)
    items = list(reversed(items))  # от старых к новым
    log.info("DA: fetched %d items (last_id=%d)", len(items), last_id)

    max_id = last_id
    for it in items:
        try:
            did = int(it.get("id") or 0)
        except Exception:
            continue
        if did <= last_id:
            continue
        if did > max_id:
            max_id = did

        amount = float(it.get("amount") or 0)
        currency = str(it.get("currency") or "RUB").upper()
        message = (it.get("message") or it.get("message_text") or it.get("text") or it.get("comment") or "")

        m = CODE_RE.search(message or "")
        if not m:
            continue
        code = m.group(1).upper()

        # --- ВАЖНО: сохраняем tg_id до закрытия сессии ---
        with Session() as db:
            p = db.query(Payment).filter_by(code=code, status="pending").one_or_none()
            if not p:
                log.info("DA: code %s not found in pending payments", code)
                continue

            min_amt = float(s.da_min_amount_rub or s.da_price_rub or 0)
            if currency != "RUB" or (min_amt and amount + 1e-9 < min_amt):
                log.info("DA: code %s amount/currency not acceptable (%.2f %s)", code, amount, currency)
                continue

            tg_id = p.tg_id  # <<< СПАСАЕМ tg_id
            p.status = "paid"
            db.commit()
            log.info("DA: code %s matched, payment marked as PAID (tg_id=%s)", code, tg_id)

        # Дальше работаем с tg_id, а не с p.*
        api = OutlineAPI(s.outline_api_url, s.outline_api_key)
        with Session() as db:
            user = db.query(User).filter_by(tg_id=tg_id).one_or_none()
            now = datetime.utcnow()
            if not user:
                user = User(tg_id=tg_id, username="")
                db.add(user); db.flush()

            until = (user.expires_at if user.expires_at and user.expires_at > now else now)
            user.expires_at = until + timedelta(days=s.default_valid_days)

            # политика 1 ключ → старый удаляем
            try:
                if user.current_key_id:
                    await api.delete_key(user.current_key_id)
            except Exception:
                pass

            name = f"user_{user.tg_id}_T1_{int(time.time())}"
            key = await api.create_key(name=name)
            user.current_key_id = key.get("id")
            user.current_key_secret = key.get("accessUrl")
            access_url = user.current_key_secret  # сохраним для отправки
            db.commit()

        await api.close()

        # отправляем ключ пользователю
        try:
            await bot.send_message(
                chat_id=tg_id,
                text=(
                    "✅ Оплата получена. Доступ активирован.\n\n"
                    "*Внимание: регенерация отключит старый ключ.*\n"
                    f"`{access_url}`"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            log.error("Send key to user failed: %s", e)

    if max_id > last_id:
        _set_kv("da_last_id", str(max_id))
        log.info("DA: updated last_id -> %d", max_id)