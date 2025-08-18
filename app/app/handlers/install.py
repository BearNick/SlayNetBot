# app/handlers/install.py
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.config import load_settings

router = Router()
s = load_settings()

@router.callback_query(F.data == "install_outline")
async def install_outline(cb: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="Android (Outline)", url=s.outline_link_android or "https://getoutline.org/get-started/#step-3")
    kb.button(text="iOS (Outline)", url=s.outline_link_ios or "https://getoutline.org/get-started/#step-3")
    kb.button(text="Desktop (Outline)", url=s.outline_link_desktop or "https://getoutline.org/get-started/#step-3")
    kb.adjust(1)
    await cb.message.answer(
        "⚡ Клиенты для *Wi-Fi (Outline)*:\n"
        "Скачай и установи подходящее приложение. После оплаты бот пришлёт `ss://` ссылку — импортируй её в клиент.",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
    await cb.answer()

@router.callback_query(F.data == "install_mobile")
async def install_mobile(cb: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="Android: v2rayNG", url=s.v2rayng_link or "https://github.com/2dust/v2rayNG/releases/latest")
    kb.button(text="FoXray", url=s.foxray_link or "https://foxray.org/#download")
    kb.button(text="Sing-box", url=s.singbox_link_ios or "https://github.com/SagerNet/sing-box")
    kb.button(text="macOS: Stash", url=s.stash_link or "https://apps.apple.com/us/app/stash-rule-based-proxy/id1596063349")
    kb.button(text="Android/Windows: Hiddify", url=s.hiddify_link or "https://github.com/hiddify/hiddify-app")
    kb.button(text="Windows/Linux/macOS: Nekoray", url=s.nekoray_link or "https://github.com/MatsuriDayo/nekoray")
    kb.button(text="iOS/Android: Karing", url=s.karing_link or "https://apps.apple.com/us/app/karing/id6472431552")
    kb.adjust(1)
    await cb.message.answer(
        "📱 Клиенты для *Wi-Fi + мобильный (Reality)*:\n"
        "Установи клиент. После оплаты бот пришлёт `vless://` ссылку — импортируй её (или отскань QR).",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
    await cb.answer()