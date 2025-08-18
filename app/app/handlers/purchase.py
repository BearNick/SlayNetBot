# app/handlers/purchase.py
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.config import load_settings
from app.storage import Session, User, KV, Payment, init_db
from datetime import datetime
import random, string

router = Router()
settings = load_settings()

def _get_mode(tg_id: int) -> str:
    with Session() as s:
        row = s.get(KV, f"mode:{tg_id}")
        return row.value if row else "outline"

def _gen_code(prefix="SLAY"):
    body = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"{prefix}-{body}"

@router.callback_query(F.data == "purchase")
async def on_purchase(cb: types.CallbackQuery):
    init_db()
    mode = _get_mode(cb.from_user.id)

    # цена: для mobile берём MOBILE_PRICE_RUB (если задана), иначе обычную
    price = (settings.mobile_price_rub if (mode == "mobile" and settings.mobile_price_rub) else settings.da_price_rub) or 0
    url = settings.da_pay_url or "https://www.donationalerts.com/r/SlayNetBot"

    # создаём pending-платёж с кодом; watcher сам подтвердит
    with Session() as s:
        code = _gen_code("SLAY")
        p = Payment(
            tg_id=cb.from_user.id,
            code=code,
            amount=float(price),
            currency="RUB",
            status="pending",
            created_at=datetime.utcnow(),
        )
        s.add(p)
        # на всякий случай дублируем выбранный режим
        key = f"mode:{cb.from_user.id}"
        row = s.get(KV, key)
        if not row:
            s.add(KV(key=key, value=mode))
        else:
            row.value = mode
        s.commit()

    kb = InlineKeyboardBuilder()
    kb.button(text=f"Оплатить {int(price)} ₽ (DonationAlerts)", url=url)
    kb.adjust(1)

    await cb.message.edit_text(
        (
            f"Режим: {'📱 Reality' if mode=='mobile' else '⚡ Outline'}\n"
            f"💳 Стоимость: {int(price)} ₽ за {settings.default_valid_days} дн.\n\n"
            f"Скопируйте и вставьте *код* в сообщение к донату: `{code}`\n"
            f"Без кода бот не сможет автоматически подтвердить оплату.\n\n"
            f"После перевода дождитесь подтверждения — ссылка придёт автоматически."
        ),
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
    await cb.answer()