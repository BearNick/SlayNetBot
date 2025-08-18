# app/bot.py
import asyncio, logging
from aiogram import Bot, Dispatcher
from app.config import load_settings
from app.storage import init_db
from app.handlers.start import router as start_router
from app.handlers.purchase import router as purchase_router
from app.handlers.account import router as account_router
from app.handlers.admin import router as admin_router
from app.handlers.install import router as install_router
from app.jobs.da_watcher import process_donations
from app.jobs.expire import loop_revoke_expired

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

async def _da_loop(bot: Bot):
    s = load_settings()
    if not s.da_access_token:
        logging.info("DA watcher disabled (no DA_ACCESS_TOKEN).")
        return
    logging.info("DA watcher started.")
    while True:
        try:
            await process_donations(bot)
        except Exception as e:
            logging.exception("DA watcher error: %s", e)
        await asyncio.sleep(max(5, s.da_poll_seconds))

async def main():
    s = load_settings()
    bot = Bot(token=s.bot_token)
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(purchase_router)
    dp.include_router(account_router)
    dp.include_router(admin_router)
    dp.include_router(install_router)
    init_db()

    me = await bot.get_me()
    logging.info(f"Bot started as @{me.username} (id={me.id})")

    # фоновая задача автоподтверждения DA
    asyncio.create_task(_da_loop(bot))

    # фоновая задача авто-деактивации просроченных Outline-ключей
    asyncio.create_task(loop_revoke_expired(bot, interval_sec=900))  # каждые 15 минут

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass