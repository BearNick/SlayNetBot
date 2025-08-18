
# Stub payment module. Replace with Stripe/Crypto integration as needed.

from dataclasses import dataclass

@dataclass
class PaymentIntent:
    amount: float
    currency: str
    months: int
    plan_code: str
    status: str = "paid"  # 'requires_payment', 'paid'

async def create_checkout(amount: float, currency: str, months: int, plan_code: str) -> PaymentIntent:
    # TODO: Integrate real provider (Stripe, Coinbase Commerce, etc.)
    return PaymentIntent(amount=amount, currency=currency, months=months, plan_code=plan_code, status="paid")
