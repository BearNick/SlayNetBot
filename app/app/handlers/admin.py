import os, time
from aiogram import Router, types
from aiogram.filters import Command
from app.storage import Session, User, init_db
from app.config import load_settings
from datetime import datetime, timedelta
from app.outline_api import OutlineAPI

router = Router()
settings = load_settings()

def _admin_ids():
    try:
        return [int(x) for x in os.getenv("ADMIN_IDS","").split(",") if x]
    except:
        return []

@router.message(Command("approve"))
async def approve_payment(msg: types.Message):
    if msg.from_user.id not in _admin_ids():
        return
    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("Использование: /approve <tg_id>")
        return
    try:
        tg_id = int(args[1])
    except ValueError:
        await msg.answer("tg_id должен быть числом")
        return

    init_db()
    with Session() as s:
        user = s.query(User).filter_by(tg_id=tg_id).one_or_none()
        if not user:
            user = User(tg_id=tg_id, username="")
            s.add(user)
            s.flush()

        add_days = settings.default_valid_days
        now = datetime.utcnow()
        if user.expires_at and user.expires_at > now:
            user.expires_at += timedelta(days=add_days)
        else:
            user.expires_at = now + timedelta(days=add_days)
        s.commit()

    # Авто-выдача ключа: удалим старый, создадим новый
    api = OutlineAPI(settings.outline_api_url, settings.outline_api_key)
    with Session() as s:
        user = s.query(User).filter_by(tg_id=tg_id).one()

        if user.current_key_id:
            try:
                await api.delete_key(user.current_key_id)
            except Exception:
                pass

        name = f"user_{user.tg_id}_T1_{int(time.time())}"
        key = await api.create_key(name=name)
        key_id = key.get("id")
        access_url = key.get("accessUrl")

        if settings.default_data_cap_gb > 0:
            bytes_limit = settings.default_data_cap_gb * (1024**3)
            try:
                await api.set_key_data_limit(key_id, bytes_limit)
            except Exception:
                pass

        user.current_key_id = key_id
        user.current_key_secret = access_url
        s.commit()

    await api.close()

    # Сообщаем админу и отправляем ключ пользователю
    await msg.answer(f"✅ Оплата подтверждена. Пользователь {tg_id} активирован до {user.expires_at:%Y-%m-%d}.\nКлюч выдан автоматически.")

    try:
        await msg.bot.send_message(
            chat_id=tg_id,
            text=(
                "✅ Оплата подтверждена. Доступ активирован.\n\n"
                "Ваш ключ готов. _Регенерация отключит старый ключ._\n"
                f"`{access_url}`"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass