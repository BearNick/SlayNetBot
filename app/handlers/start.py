from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(CommandStart())
async def start(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="Купить (1 месяц)", callback_data="purchase")
    kb.button(text="Регенерировать ключ (отключит старый)", callback_data="genkey")
    kb.button(text="Как установить Outline", callback_data="install")
    kb.adjust(1)
    txt = (
        "🤖 SlayNet VPN бот\n\n"
        "• Подписка: 1 месяц\n"
        "• Устройства: 1\n\n"
        "Оплатите, дождитесь подтверждения — бот сразу выдаст ключ.\n"
        "_Регенерация отключит старый ключ._"
    )
    await message.answer(txt, reply_markup=kb.as_markup())