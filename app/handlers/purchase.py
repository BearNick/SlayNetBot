# app/handlers/purchase.py
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.config import load_settings
from app.storage import Session, User, Payment, init_db
import random, string

router = Router()

def _make_code(tg_id: int) -> str:
    suf = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"SLAY-{suf}"

@router.callback_query(F.data == "purchase")
async def on_purchase(cb: types.CallbackQuery):
    s = load_settings()
    price = getattr(s, "da_price_rub", 0) or 0
    url = getattr(s, "da_pay_url", None) or "https://www.donationalerts.com/r/SlayNetBot"

    init_db()
    code = _make_code(cb.from_user.id)

    with Session() as db:
        # создадим пользователя в БД, если его не было
        u = db.query(User).filter_by(tg_id=cb.from_user.id).one_or_none()
        if not u:
            u = User(tg_id=cb.from_user.id, username=cb.from_user.username or "")
            db.add(u)
            db.flush()
        # создаём платёжную заявку (pending)
        p = Payment(tg_id=cb.from_user.id, code=code, amount=price, currency="RUB", status="pending")
        db.add(p)
        db.commit()

    kb = InlineKeyboardBuilder()
    kb.button(text=f"Оплатить {price} ₽ (DonationAlerts)", url=url)
    kb.adjust(1)

    await cb.message.edit_text(
        f"💳 Стоимость: {price} ₽ за 1 месяц.\n\n"
        "👉 *Важно:* при оплате укажите в *сообщении к платежу* следующий код:\n"
        f"`{code}`\n\n"
        "После оплаты бот автоматически подтвердит платёж и отправит рабочий ключ.\n"
        "Если что-то пошло не так — напишите администратору.",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
    await cb.answer()

@router.callback_query(F.data == "genkey")
async def on_genkey(cb: types.CallbackQuery):
    # Ручная регенерация (при активной подписке)
    from datetime import datetime
    from app.outline_api import OutlineAPI

    s = load_settings()
    init_db()

    with Session() as db:
        u = db.query(User).filter_by(tg_id=cb.from_user.id).one_or_none()
        if not u or not u.expires_at or u.expires_at < datetime.utcnow():
            await cb.message.answer("Сначала оплатите подписку — или дождитесь авто-подтверждения платежа.")
            await cb.answer(); return

    api = OutlineAPI(s.outline_api_url, s.outline_api_key)
    with Session() as db:
        u = db.query(User).filter_by(tg_id=cb.from_user.id).one()
        if u.current_key_id:
            try:
                await api.delete_key(u.current_key_id)
            except Exception:
                pass
        name = f"user_{u.tg_id}_T1"
        key = await api.create_key(name=name)
        u.current_key_id = key.get("id")
        u.current_key_secret = key.get("accessUrl")
        db.commit()
    await api.close()

    await cb.message.answer(
        "Ваш ключ готов. Нажмите ссылку ниже — Outline импортирует конфиг автоматически.\n\n"
        "*Внимание: регенерация отключит старый ключ.*\n"
        f"`{u.current_key_secret}`",
        parse_mode="Markdown"
    )
    await cb.answer()