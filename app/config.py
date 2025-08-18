# app/config.py
from pydantic import BaseModel
import os

class Settings(BaseModel):
    bot_token: str
    admin_ids: list[int]
    outline_api_url: str
    outline_api_key: str | None = None

    # Business
    default_valid_days: int = 30
    allowed_prepaid_months: list[int] = [1]
    default_data_cap_gb: int = 0

    # DonationAlerts (UI)
    da_pay_url: str | None = None
    da_price_rub: int = 0

    # DonationAlerts (API)
    da_access_token: str | None = None
    da_poll_seconds: int = 20
    da_min_amount_rub: int = 0

def _parse_list_int(val: str, default: list[int]):
    try:
        return [int(x.strip()) for x in val.split(",") if x.strip()]
    except:
        return default

def _parse_admin_ids(val: str):
    try:
        return [int(x.strip()) for x in val.split(",") if x.strip()]
    except:
        return []

def load_settings() -> Settings:
    from dotenv import load_dotenv
    load_dotenv()
    url = os.getenv("OUTLINE_API_URL","").rstrip("/")
    return Settings(
        bot_token=os.getenv("BOT_TOKEN",""),
        admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS","")),
        outline_api_url=url,
        outline_api_key=(os.getenv("OUTLINE_API_KEY","") or None),

        default_valid_days=int(os.getenv("DEFAULT_VALID_DAYS","30")),
        allowed_prepaid_months=_parse_list_int(os.getenv("ALLOWED_PREPAID_MONTHS","1"), [1]),
        default_data_cap_gb=int(os.getenv("DEFAULT_DATA_CAP_GB","0")),

        da_pay_url=os.getenv("DA_PAY_URL"),
        da_price_rub=int(os.getenv("DA_PRICE_RUB","0")),

        da_access_token=os.getenv("DA_ACCESS_TOKEN") or None,
        da_poll_seconds=int(os.getenv("DA_POLL_SECONDS","20")),
        da_min_amount_rub=int(os.getenv("DA_MIN_AMOUNT_RUB","0")),
    )