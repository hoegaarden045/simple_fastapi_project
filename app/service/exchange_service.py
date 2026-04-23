from decimal import Decimal
from typing import Dict, Tuple

import requests
from app.enums import CurrencyEnum

FALLBACK_RATES: Dict[Tuple[str, str], Decimal] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): Decimal(str(95.0)),
    (CurrencyEnum.USD, CurrencyEnum.EUR): Decimal(str(0.92)),
    (CurrencyEnum.EUR, CurrencyEnum.RUB): Decimal(str(103.26)),
    (CurrencyEnum.RUB, CurrencyEnum.USD): Decimal(str(0.0105)),
    (CurrencyEnum.EUR, CurrencyEnum.USD): Decimal(str(1.087)),
    (CurrencyEnum.RUB, CurrencyEnum.EUR): Decimal(str(0.0097)),
}


def get_exchange_rate(base: CurrencyEnum, target: CurrencyEnum) -> Decimal:

    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        base_map = data.get(base, {})
        rate = base_map.get(target)

        if rate is not None and isinstance(rate, (int, float)):
            return Decimal(rate)
        raise KeyError("Rate not found")

    except Exception:
        return FALLBACK_RATES.get((base, target), Decimal(1))
