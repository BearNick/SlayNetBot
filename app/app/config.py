# app/config.py
from pydantic import BaseModel
import os
from typing import Optional  # на случай pydantic v1

from dotenv import load_dotenv
load_dotenv()

class Settings(BaseModel):
    bot_token: str
    admin_ids: list[int] = []
    outline_api_url: str = ""
    outline_api_key: str = ""
    default_valid_days: int = 30

    da_price_rub: float = 0.0
    da_min_amount_rub: float = 0.0      # минимальная сумма для засчёта доната
    da_pay_url: str = ""
    da_access_token: str = ""           # для DA watcher
    da_poll_seconds: int = 20           # ← ДОБАВИЛИ: период опроса DA (сек)

    # (опционально, если где-то остался лимит трафика для Outline)
    default_data_cap_gb: float = 0.0

    # Мобильный режим (VLESS/REALITY)
    mobile_vless_uri: str = ""
    mobile_price_rub: Optional[float] = None  # или: float | None, если pydantic v2

    outline_link_android: str = ""
    outline_link_ios: str = ""
    outline_link_desktop: str = ""

    v2rayng_link: str = ""
    foxray_link: str = ""
    singbox_link_ios: str = ""
    stash_link: str = ""
    hiddify_link: str = ""
    nekoray_link: str = ""
    karing_link: str = ""

def load_settings() -> Settings:
    def _get(name, default=""):
        return os.getenv(name, default)

    admin_ids_str = _get("ADMIN_IDS", "")
    admin_ids = [int(x) for x in admin_ids_str.replace(" ", "").split(",") if x]

    return Settings(
        bot_token=_get("BOT_TOKEN"),
        admin_ids=admin_ids,
        outline_api_url=_get("OUTLINE_API_URL", ""),
        outline_api_key=_get("OUTLINE_API_KEY", ""),
        default_valid_days=int(_get("DEFAULT_VALID_DAYS", "30")),

        da_price_rub=float(_get("DA_PRICE_RUB", "0")),
        da_min_amount_rub=float(_get("DA_MIN_AMOUNT_RUB", "0")),
        da_pay_url=_get("DA_PAY_URL", ""),
        da_access_token=_get("DA_ACCESS_TOKEN", ""),
        da_poll_seconds=int(_get("DA_POLL_SECONDS", "20")),   # ← ДОБАВИЛИ загрузку из .env

        default_data_cap_gb=float(_get("DEFAULT_DATA_CAP_GB", "0")),

        mobile_vless_uri=_get("MOBILE_VLESS_URI", ""),
        mobile_price_rub=(float(_get("MOBILE_PRICE_RUB")) if _get("MOBILE_PRICE_RUB") else None),

        outline_link_android=_get("OUTLINE_LINK_ANDROID", "https://getoutline.org/get-started/#step-3"),
        outline_link_ios=_get("OUTLINE_LINK_IOS", "https://getoutline.org/get-started/#step-3"),
        outline_link_desktop=_get("OUTLINE_LINK_DESKTOP", "https://getoutline.org/get-started/#step-3"),

        v2rayng_link=_get("V2RAYNG_LINK", "https://github.com/2dust/v2rayNG/releases/latest"),
        foxray_link=_get("FOXRAY_LINK", "https://foxray.org/#download"),
        singbox_link_ios=_get("SINGBOX_LINK_IOS", "https://github.com/SagerNet/sing-box"),
        stash_link=_get("STASH_LINK", "https://apps.apple.com/us/app/stash-rule-based-proxy/id1596063349"),
        hiddify_link=_get("HIDDIFY_LINK", "https://github.com/hiddify/hiddify-app"),
        nekoray_link=_get("NEKORAY_LINK", "https://github.com/MatsuriDayo/nekoray"),
        karing_link=_get("KARING_LINK", "https://apps.apple.com/us/app/karing/id6472431552"),
    )