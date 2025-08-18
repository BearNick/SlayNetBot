# app/handlers/start.py
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.storage import Session, User, KV, init_db

router = Router()

def _set_mode(tg_id: int, mode: str):
    with Session() as s:
        key = f"mode:{tg_id}"
        row = s.get(KV, key)
        if not row:
            s.add(KV(key=key, value=mode))
        else:
            row.value = mode
        s.commit()

@router.message(CommandStart())
async def cmd_start(m: types.Message):
    init_db()
    with Session() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).one_or_none()
        if not u:
            u = User(tg_id=m.from_user.id, username=m.from_user.username or "")
            s.add(u)
            s.commit()

    kb = InlineKeyboardBuilder()
    kb.button(text="⚡ VPN для Wi-Fi (Outline)", callback_data="mode_outline")
    kb.button(text="📱 VPN Wi-Fi + мобильный (Reality)", callback_data="mode_mobile")
    kb.adjust(1)
    await m.answer(
        "Привет! Выбери режим подключения:\n\n"
        "⚡ *Wi-Fi (Outline)* — простой и быстрый, лучше для Wi-Fi.\n"
        "📱 *Wi-Fi + мобильный (Reality)* — устойчив к блокировкам операторов связи.\n",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data == "mode_outline")
async def on_mode_outline(cb: types.CallbackQuery):
    _set_mode(cb.from_user.id, "outline")
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Купить доступ (Outline)", callback_data="purchase")
    kb.button(text="📥 Клиенты (Outline)", callback_data="install_outline")  # ← ДОБАВЛЕНО
    kb.adjust(1)
    await cb.message.edit_text(
        "Режим: ⚡ *Wi-Fi (Outline)*.\n\nНажми кнопку ниже для оплаты:",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
    await cb.answer()

@router.callback_query(F.data == "mode_mobile")
async def on_mode_mobile(cb: types.CallbackQuery):
    _set_mode(cb.from_user.id, "mobile")
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Купить доступ (Reality)", callback_data="purchase")
    kb.button(text="📥 Клиенты (Reality)", callback_data="install_mobile")   # ← ДОБАВЛЕНО
    kb.adjust(1)
    await cb.message.edit_text(
        "Режим: 📱 *Wi-Fi + мобильный (Reality)*.\n\n"
        "Нужен клиент: *v2rayNG (Android), FoXray/Sing-box (iOS), v2rayN (Windows), Stash (macOS)*.\n"
        "Нажми кнопку ниже для оплаты:",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
    await cb.answer()