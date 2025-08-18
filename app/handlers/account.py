
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.storage import Session, User, days_left, init_db

router = Router()

@router.callback_query(F.data=="account")
async def on_account(cb: types.CallbackQuery):
    init_db()
    with Session() as s:
        user = s.query(User).filter_by(tg_id=cb.from_user.id).one_or_none()
        if not user:
            await cb.message.answer("Аккаунт не найден. Нажмите Purchase, чтобы купить доступ.")
            return
        left = days_left(user)
        txt = (
            f"Тариф: {user.plan_code}\n"
            f"Дней осталось: {left}\n"
            f"Ключ: {'есть' if user.current_key_id else 'не сгенерирован'}"
        )
        kb = InlineKeyboardBuilder()
        kb.button(text="Сгенерировать новый ключ", callback_data="genkey")
        kb.button(text="Установить приложение", callback_data="install")
        kb.adjust(1)
        await cb.message.answer(txt, reply_markup=kb.as_markup())

@router.callback_query(F.data=="install")
async def on_install(cb: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="iOS", callback_data="install_ios")
    kb.button(text="Android", callback_data="install_android")
    kb.button(text="Desktop", callback_data="install_desktop")
    kb.adjust(3)
    await cb.message.answer("Выберите платформу:", reply_markup=kb.as_markup())

@router.callback_query(F.data=="install_ios")
async def on_install_ios(cb: types.CallbackQuery):
    from app.utils.links import OUTLINE_LINKS
    # App Store link opens the store app directly
    await cb.message.answer(f"Установите из App Store: {OUTLINE_LINKS['ios']}")
    await cb.answer()

@router.callback_query(F.data=="install_android")
async def on_install_android(cb: types.CallbackQuery):
    from app.utils.links import OUTLINE_LINKS
    await cb.message.answer(f"Установите из Google Play: {OUTLINE_LINKS['android']}")
    await cb.answer()

@router.callback_query(F.data=="install_desktop")
async def on_install_desktop(cb: types.CallbackQuery):
    from app.utils.links import OUTLINE_LINKS
    await cb.message.answer(
        "Windows/macOS/Linux: зайдите на релизы Outline Client и скачайте дистрибутив для вашей ОС:\n"
        f"{OUTLINE_LINKS['windows']}"
    )
    await cb.answer()
